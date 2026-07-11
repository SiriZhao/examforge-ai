FROM node:20-bookworm-slim AS frontend-build

WORKDIR /workspace/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend ./
ENV VITE_API_BASE_URL=
ENV VITE_APP_NAME="Campus AI Workspace"
ENV VITE_APP_VERSION=0.5.1
RUN npm run build

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV APP_MODE=cloud
ENV APP_NAME="Campus AI Workspace"
ENV APP_VERSION=0.5.1
ENV PORT=8000
ENV STORAGE_DIR=/data
ENV UPLOAD_DIR=uploads
ENV OUTPUT_DIR=outputs
ENV OCR_CACHE_DIR=cache/ocr

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    fonts-noto-cjk \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libcairo2 \
    libffi8 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY --from=frontend-build /workspace/frontend/dist ./app/static

RUN mkdir -p /data/uploads /data/outputs /data/cache/ocr
RUN useradd --create-home --uid 10001 campus && chown -R campus:campus /app /data

USER campus

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/api/health', timeout=3)"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
