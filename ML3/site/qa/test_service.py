"""Regression tests for transport limits, service boundaries and checkpoint integrity.
Run: python -m unittest discover -s ML3/site/qa -p test_service.py -v
"""
import sys, io, unittest, hashlib, json
from pathlib import Path
from unittest.mock import patch
from fastapi.testclient import TestClient
from PIL import Image
API = Path(__file__).resolve().parents[1] / 'api'
sys.path.insert(0, str(API))
import app as service

class ServiceTests(unittest.TestCase):
    def setUp(self):
        service._hits.clear()
        self.client = TestClient(service.app)

    def test_health_and_info(self):
        self.assertEqual(self.client.get('/api/health').json()['status'], 'ok')
        self.assertEqual(len(self.client.get('/api/info').json()['models']), 4)

    def test_internal_files_are_not_public(self):
        for path in ['/api/app.py', '/api/models/models.json', '/api/models/effnet_full_E0_pooled_s0.pt', '/qa/test_service.py']:
            self.assertEqual(self.client.get(path).status_code, 404, path)

    def test_public_pages_and_openapi(self):
        for page in API.parent.glob('*.html'):
            response = self.client.get('/' + page.name)
            self.assertEqual(response.status_code, 200)
            self.assertIn('nosniff', response.headers['x-content-type-options'])
        self.assertEqual(self.client.get('/api/openapi.json').status_code, 200)
        self.assertEqual(self.client.get('/downloads/audit_results.py').status_code, 200)

    def test_bad_image(self):
        self.assertEqual(self.client.post('/api/predict',content=b'not an image',headers={'content-type':'image/png'}).status_code,400)

    def test_probe_flags_shortcut_compatible_prediction(self):
        import probe
        facts = dict(width=640, height=640, aspect=1.0, format='JPEG', mode='RGB', file_kb=36.3)   # typical AV-DDH (hip) file
        fake = lambda pred: dict(models=[dict(id='pooled', pred=pred)] + [dict(id=f'm{i}', pred=pred) for i in range(3)])
        out = probe.run(facts, fake('Hip'))
        self.assertTrue(out['available'] and out['in_range'])
        self.assertEqual(out['joint']['pred'], 'Hip'); self.assertEqual(out['source']['id'], 'A')
        self.assertEqual(out['verdict']['level'], 'shortcut')
        self.assertEqual(probe.run(facts, fake('Shoulder'))['verdict']['level'], 'independent')

    def test_probe_marks_unfamiliar_files(self):
        import probe
        facts = dict(width=5000, height=4000, aspect=1.25, format='JPEG', mode='L', file_kb=9000.0)
        out = probe.run(facts, dict(models=[dict(id='pooled', pred='Hip')] * 4))
        self.assertEqual(out['verdict']['level'], 'unfamiliar'); self.assertFalse(out['in_range'])

    def test_predict_response_includes_probe(self):
        buf = io.BytesIO(); Image.new('L', (640, 640), 90).save(buf, 'PNG')
        response = self.client.post('/api/predict', content=buf.getvalue(), headers={'content-type': 'image/png'})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertTrue(body['probe']['available']); self.assertIn(body['probe']['verdict']['level'], {'shortcut', 'weak', 'independent', 'unfamiliar'})
        self.assertNotIn('path', json.dumps(body['probe']).lower())

    def test_invalid_content_length(self):
        for length in ['invalid', '-1']:
            self.assertEqual(self.client.post('/api/predict',content=b'',headers={'content-type':'image/png','content-length':length}).status_code,400)

    def test_stream_without_length_is_bounded(self):
        response=self.client.post('/api/predict',content=iter([b'x'*(1024*1024)]*13),headers={'content-type':'image/png'})
        self.assertEqual(response.status_code,413)

    def test_missing_models_explicit(self):
        with patch.object(service.infer, 'available', return_value=False):
            self.assertEqual(self.client.get('/api/health').json()['status'],'models_missing')
            self.assertEqual(self.client.post('/api/predict',content=b'x',headers={'content-type':'image/png'}).status_code,503)

    def test_rate_limit(self):
        for _ in range(30): self.client.post('/api/predict',content=b'x')
        self.assertEqual(self.client.post('/api/predict',content=b'x').status_code,429)

    def test_model_hashes_match_supplied_registry(self):
        registry=json.loads((API/'models/models.json').read_text())
        for spec in service.infer.SPEC:
            key=spec[3].removeprefix('effnet_full_').removesuffix('.pt')
            self.assertEqual(hashlib.sha256((API/'models'/spec[3]).read_bytes()).hexdigest(),registry[key]['sha256'])

    def test_preprocessing_shape_and_determinism(self):
        image=Image.new('L',(123,97),128)
        a=service.infer.preprocess(image)
        self.assertEqual(tuple(a.shape),(1,3,160,160))
        self.assertTrue(a.equal(service.infer.preprocess(image)))

if __name__=='__main__': unittest.main()
