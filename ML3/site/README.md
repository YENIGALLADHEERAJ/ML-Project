# OrthoTrace — research demonstration site

Updated product workbench: start from `D:\ML Project` with `start.ps1`. See `../docs/DELIVERY.md` for the tested environment, changes, full verification and remaining evidence gaps; `../../README.md` provides the Windows commands. The active landing page source is `reference_home.html.template`; the final visual layer is `assets/css/reference.css`. See `../docs/FRONTEND_DELIVERY.md` for the 16-page experience, interactive implant history and final browser verification.

Static multi-page site (`*.html`, `assets/`, `data/`) + a small FastAPI inference service (`api/`) serving the same four study checkpoints on CPU.
**Research demonstration only. Not a medical device, not clinically validated.**

## Run locally
```bash
pip install -r api/requirements.txt        # torch 2.4.1 CPU is enough
cd api && uvicorn app:app --port 8000      # site + API at http://localhost:8000
```
If the API is not reachable the AI Demo switches itself to a clearly labelled *precomputed* mode (real checkpoint outputs for 9 held-out FracAtlas images); uploads are then disabled. Pages and charts are fully static and work from any web host.

## Deploy
* Docker (self-contained, ~1 GB with CPU torch): `docker build -t orthotrace .` then `docker run -p 8000:8000 orthotrace`. Works on any container host (Fly.io, Render, Cloud Run, a VPS).
* Static-only hosting (GitHub Pages, Netlify): upload everything except `api/`; the demo runs in precomputed mode.
* Put the container behind HTTPS; the API keeps no files, logs no images, limits 12 MB per upload and 30 requests/min/IP.

## Rebuild pages / data
`python build_data.py` (reads `../artifacts`, regenerates `data/results.json`) and `python build_site.py` (regenerates the pages and copies manuscript, figures and docs into `downloads/` and `assets/figures/`).
All numbers on the site come from `data/results.json`, which is generated from the frozen study artifacts; nothing is typed in by hand except narrative text.

## Frontend stack (motion layer)
Vanilla JS + CSS; animation by GSAP 3.12 + ScrollTrigger and Lenis 1.1 (vendored in `assets/vendor/`, no CDN needed; GSAP under GreenSock's standard licence, Lenis MIT). Hero particles are a 2D canvas (no WebGL: nothing here needs it). Honors `prefers-reduced-motion` (no smooth scroll, pinning, curtain or particles) and works without JS. Fonts (Instrument Serif, Inter, JetBrains Mono) load from Google Fonts with system fallbacks.

## Production pass (QA)
* `qa/qa_audit.py` - static audit of the built pages: every hard-coded number in the narrative vs `data/results.json`, disclaimer on every page, one h1 / valid heading outline, unique ids, alt text, button names, internal links and asset references, only Google Fonts as external requests.
* `qa/qa_api.py` - live API checks: the 9 shipped sample JPEGs reproduce the precomputed outputs exactly, Grad-CAM present, PNG/colour/tiny/huge/odd-type inputs handled.
* `qa/qa_dom.js` - layout audit run in the browser (overflow, broken images, small touch targets, heading clipping) at 375 / 768 / 1280 px.
* `DEPLOY.md` - exact deployment instructions (Docker, VPS + Caddy, Fly.io / Render / Cloud Run, static-only).
