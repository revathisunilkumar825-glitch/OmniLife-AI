# OmniLife AI - backend image (FastAPI + AI libraries)
# Build:  docker build -t omnilife-backend .
# Run:    docker run -p 8000:8000 --env-file .env omnilife-backend
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# libglib/libgomp are needed by OpenCV / PyTorch / FAISS at runtime
RUN apt-get update \
    && apt-get install -y --no-install-recommends libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first so Docker caches this slow layer.
# CPU-only PyTorch keeps the image several GB smaller than the default CUDA build.
COPY requirements.txt .
RUN pip install --extra-index-url https://download.pytorch.org/whl/cpu -r requirements.txt

COPY backend ./backend
COPY ai ./ai
COPY database ./database
COPY documents ./documents

# Security: do not run the web server as root.
RUN useradd --create-home appuser \
    && mkdir -p /app/uploads/pdf /app/uploads/images \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Tiny liveness check (backend/main.py should expose GET /health)
HEALTHCHECK --interval=30s --timeout=5s --start-period=60s \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status==200 else 1)"

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
