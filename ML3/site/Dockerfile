# OrthoTrace research demo (CPU only). Build context = this folder (site/).
#   docker build -t orthotrace .
#   docker run --rm -p 8000:8000 orthotrace          ->  http://localhost:8000
FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=2 PIP_NO_CACHE_DIR=1 PIP_DEFAULT_TIMEOUT=120 PIP_RETRIES=10
RUN pip install fastapi "uvicorn[standard]" pillow numpy opencv-python-headless \
 && pip install torch==2.4.1 torchvision==0.19.1 --index-url https://download.pytorch.org/whl/cpu
RUN useradd -m -u 10001 app
WORKDIR /srv/site
COPY --chown=app:app . /srv/site
USER app
WORKDIR /srv/site/api
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=40s CMD python -c "import urllib.request,sys;sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=4).status==200 else 1)"
CMD ["uvicorn","app:app","--host","0.0.0.0","--port","8000","--proxy-headers","--forwarded-allow-ips","*"]
