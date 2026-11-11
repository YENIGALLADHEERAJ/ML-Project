"""FastAPI service: serves the static research site and a minimal inference API for the research demo.
Run:  uvicorn app:app --host 0.0.0.0 --port 8000     (from site/api)   -> site at http://localhost:8000
Privacy: uploaded images are decoded in memory and discarded; nothing is written to disk or logged. Not a medical device."""
import io, time, collections
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from PIL import Image, UnidentifiedImageError
import infer
import probe
from starlette.concurrency import run_in_threadpool
from threading import Lock

INFERENCE_LOCK = Lock()

def analyse(img):
    # Grad-CAM installs hooks and mutates gradients on shared model instances.
    with INFERENCE_LOCK:
        return infer.predict(img)

SITE = Path(__file__).resolve().parents[1]; MAX_BYTES = 12 * 1024 * 1024; ALLOWED = {"image/jpeg", "image/png", "image/bmp", "image/webp", "image/tiff"}
DISCLAIMER = "Academic project. Not a medical device, not validated for clinical use, and not a diagnosis. Do not upload images that could identify a patient."
app = FastAPI(title="OrthoTrace project API", version="1.0", docs_url="/api/docs", openapi_url="/api/openapi.json", redoc_url=None)
app.add_middleware(GZipMiddleware, minimum_size=800)


@app.middleware("http")
async def headers(request: Request, call_next):
    p = request.url.path
    if (p.startswith('/api/') and p not in {'/api/health', '/api/info', '/api/predict', '/api/docs', '/api/openapi.json'}) or p.startswith('/qa/') or (p.endswith(('.py', '.pt', '.jsonl')) and not p.startswith('/downloads/')):
        return JSONResponse({'error': 'not_found'}, status_code=404)
    resp = await call_next(request); p = request.url.path
    resp.headers.update({"X-Content-Type-Options": "nosniff", "Referrer-Policy": "strict-origin-when-cross-origin", "X-Frame-Options": "DENY", "Permissions-Policy": "camera=(), microphone=(), geolocation=()"})
    if p.startswith("/api/"): resp.headers["Cache-Control"] = "no-store"
    elif "v" in request.query_params and p.startswith("/assets/"): resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"  # content-hashed URL
    elif p.startswith(("/assets/", "/downloads/")): resp.headers["Cache-Control"] = "public, max-age=3600, must-revalidate"
    elif p.endswith((".html", "/")) or p.startswith("/data/"): resp.headers["Cache-Control"] = "no-cache"
    return resp
_hits = collections.defaultdict(list)


def limited(ip, n=30, per=60):
    now = time.monotonic()
    for key in list(_hits):
        if not _hits[key] or now - _hits[key][-1] >= per: del _hits[key]
    h = [t for t in _hits[ip] if now - t < per]; _hits[ip] = h
    if len(h) >= n: return True
    h.append(now); return False


@app.get("/api/health")
def health():
    return dict(status="ok" if infer.available() else "models_missing", models=infer.model_hashes() if infer.available() else {}, device="cpu", expanded_available=infer.region_available(), disclaimer=DISCLAIMER)


@app.get("/api/info")
def info():
    return dict(models=[dict(id=s[0], name=s[1], description=s[2]) for s in infer.SPEC], classes=infer.CL, expanded_available=infer.region_available(), input="grey, stretched to 160x160, ImageNet-normalised (identical to the study)", disclaimer=DISCLAIMER,
                notes=["Probabilities are raw softmax outputs; they are not calibrated and are unreliable under source shift (see Results).", "Expanded anatomy scores are independent sigmoid outputs with per-class cutoffs.", "The heat map is a Grad-CAM of the pooled model's last convolutional block; it does not prove what the model 'reasons' with."])


@app.post("/api/predict")
async def predict(request: Request):
    ip = request.client.host if request.client else "?"
    if limited(ip): return JSONResponse(dict(error="rate_limited", message="Too many requests; please wait a minute."), status_code=429)
    ctype = (request.headers.get("content-type") or "").split(";")[0].strip().lower()
    if ctype not in ALLOWED: return JSONResponse(dict(error="unsupported_type", message="Send the raw image bytes with a content-type of image/jpeg, image/png, image/webp, image/bmp or image/tiff."), status_code=415)
    try:
        size = int(request.headers.get('content-length') or 0)
        if size < 0: raise ValueError()
    except ValueError:
        return JSONResponse(dict(error='bad_length', message='Invalid Content-Length.'), status_code=400)
    if size > MAX_BYTES: return JSONResponse(dict(error="too_large", message="Image larger than 12 MB."), status_code=413)
    raw = bytearray()
    async for chunk in request.stream():
        if len(raw) + len(chunk) > MAX_BYTES:
            return JSONResponse(dict(error='too_large', message='Image larger than 12 MB.'), status_code=413)
        raw.extend(chunk)
    raw = bytes(raw)
    if not infer.available(): return JSONResponse(dict(error="models_missing", message="Model files are not installed on this server; use the precomputed samples."), status_code=503)
    try:
        img = Image.open(io.BytesIO(raw)); img.load()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        return JSONResponse(dict(error="bad_image", message="Could not read this file as an image."), status_code=400)
    if min(img.size) < 64: return JSONResponse(dict(error="too_small", message="Image is smaller than 64 pixels on one side."), status_code=400)
    facts = infer.image_facts(raw, img); warnings = []
    if facts["colour_saturation"] > 0.12: warnings.append("This looks like a colour photograph or screenshot rather than a radiograph; the models were trained on greyscale radiographs.")
    out = await run_in_threadpool(analyse, img); out.update(image=facts, warnings=warnings, disclaimer=DISCLAIMER, stored=False)
    try:
        out["probe"] = probe.run(facts, out)   # anatomy-free shortcut probe; never blocks the main prediction
    except Exception:
        out["probe"] = dict(available=False)
    return out


app.mount("/", StaticFiles(directory=str(SITE), html=True), name="site")
