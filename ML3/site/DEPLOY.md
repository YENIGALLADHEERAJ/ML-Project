# Deploying OrthoTrace

One container serves the static site **and** the CPU inference API (five checkpoints, about 217 MB). Nothing is stored; no database; no secrets.
Needs ~1.5 GB RAM, 1 vCPU (inference ≈ 1–3 s per image on CPU), ~2 GB disk for the image.

> This deployment runs an academic anatomy and model-evaluation workbench.

## 0. Before you deploy (once)
```bash
cd site
python build_data.py        # regenerates data/results.json from the frozen artifacts (only if artifacts changed)
python build_site.py        # regenerates pages, content-hashed asset URLs, WebP figures, downloads/
python qa/qa_audit.py          # static QA: numbers vs results.json, disclaimers, links, alt text, headings (must print ALL CHECKS PASSED)
# with the server running on :8000:
python qa/qa_api.py            # API QA: live predictions reproduce the precomputed samples, bad-input handling
```

## 1. Local container test
```bash
cd site
docker build -t orthotrace .
docker run --rm -p 8000:8000 orthotrace
# open http://localhost:8000   and check  http://localhost:8000/api/health  ->  {"status":"ok", ...}
```
The image runs as a non-root user, has a health check, gzip, security headers and long-lived caching for content-hashed assets.

## 2. Deploy on a VPS with a domain (recommended: Caddy gives automatic HTTPS)
```bash
# on the server (Ubuntu/Debian): install Docker, copy the site/ folder (rsync/scp/git), then
cd site && docker build -t orthotrace .
docker run -d --name orthotrace --restart unless-stopped -p 127.0.0.1:8000:8000 orthotrace

# /etc/caddy/Caddyfile
your-domain.org {
    reverse_proxy 127.0.0.1:8000
    request_body { max_size 13MB }
}
sudo systemctl reload caddy
```
Point the domain's A/AAAA record at the server first. The app trusts `X-Forwarded-For` from the proxy for its per-IP rate limit (30 requests/min).

## 3. Managed container hosts
* **Fly.io:** `fly launch --no-deploy` (accept the Dockerfile, internal port 8000, 1 GB+ RAM) → `fly deploy`.
* **Render / Railway:** new *Web Service* from the repo's `site/` directory, runtime *Docker*, port 8000, instance ≥ 2 GB RAM.
* **Google Cloud Run:** `gcloud run deploy orthotrace --source . --port 8000 --memory 2Gi --cpu 1 --allow-unauthenticated --max-instances 2`.
Accounts, billing and credentials are yours to create; nothing in this repository contains any.

## 4. Static-only fallback (no inference)
Upload everything in `site/` **except** `api/` to any static host (GitHub Pages, Netlify, Cloudflare Pages). The AI Demo then runs in clearly labelled *precomputed* mode (real checkpoint outputs for 9 held-out images); upload is disabled.

## 5. Post-deploy smoke test
```bash
curl -s https://your-domain.org/api/health                  # status ok + checkpoint hashes
curl -s -X POST -H "Content-Type: image/jpeg" --data-binary @assets/samples/sample5.jpg https://your-domain.org/api/predict | head -c 300
curl -sI https://your-domain.org/ | grep -i "x-frame\|nosniff\|cache-control"
```
Then open every page once on a phone and a desktop browser; run the demo with a sample and with an upload.

## 6. Updating
Rebuild (`python build_site.py`), rebuild the image, restart the container. Asset URLs carry a content hash, so browsers pick up new CSS/JS immediately.

## 7. Operating notes
* Privacy: uploads are decoded in memory and discarded; the server does not log images. Keep reverse-proxy access logs free of request bodies. Tell users not to upload identifiable images (the page already does).
* Capacity: CPU-only, one image at a time per worker. For more traffic run 2–3 container replicas behind the proxy; do not add GPU.
* Licences: GSAP (GreenSock standard licence) and Lenis (MIT) are vendored in `assets/vendor/`; fonts are loaded from Google Fonts (swap to self-hosted files if you need zero third-party requests). Sample images are FracAtlas (CC BY 4.0).
* Do not present the demo as a clinical tool. The knee labels of the sample images are provisional until clinician verification (see `clinician_review/`).
