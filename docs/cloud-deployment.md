# ExamForge AI Cloud Deployment

ExamForge AI can run as a single Docker web app. The FastAPI backend serves both the API and the built frontend, so users only need a browser URL.

## Architecture

- FastAPI serves `/api/*`, uploads, generation jobs, downloads, and the frontend SPA.
- `frontend/dist` is copied into `backend/app/static` during Docker build.
- Runtime files are written under `STORAGE_DIR`:
  - `UPLOAD_DIR`
  - `OUTPUT_DIR`
  - `OCR_CACHE_DIR`
- Temporary files are removed according to `TEMP_FILE_TTL_HOURS`.
- Windows exe packaging remains available through `scripts/build-windows.ps1`.

## Docker

```bash
docker build -t examforge-ai:0.4.1 .
docker run --rm -p 8000:8000 --env-file .env.example examforge-ai:0.4.1
```

Open:

- `http://127.0.0.1:8000`
- `http://127.0.0.1:8000/api/health`

## Required Environment Variables

```env
APP_MODE=cloud
PORT=8000
PUBLIC_BASE_URL=
CORS_ORIGINS=
MAX_UPLOAD_MB=50
MAX_FILES_PER_REQUEST=10
JOB_TIMEOUT_SECONDS=600
TEMP_FILE_TTL_HOURS=24
STORAGE_DIR=/data
UPLOAD_DIR=uploads
OUTPUT_DIR=outputs
OCR_CACHE_DIR=cache/ocr
DEFAULT_LLM_PROVIDER=deepseek
DEFAULT_LLM_MODEL=deepseek-v4-flash
DEFAULT_LLM_BASE_URL=https://api.deepseek.com
DEEPSEEK_API_KEY=
OPENAI_API_KEY=
ENABLE_RAPIDOCR=true
ENABLE_TESSERACT=false
ENABLE_CLOUD_SAFE_MODE=true
LLM_CONTEXT_BUDGET_CHARS=120000
LLM_CHUNK_CHARS=18000
LLM_CHUNK_OVERLAP_CHARS=1200
LLM_MAX_CHUNKS_PER_ROUND=8
LLM_MAX_REPAIR_CALLS=1
LLM_ENABLE_CHUNK_SUMMARY=true
LLM_ENABLE_FINAL_SYNTHESIS=true
```

Do not put real API keys into git. Configure `DEEPSEEK_API_KEY` or `OPENAI_API_KEY` in the hosting platform secret manager.

## LLM Key Modes

1. User-provided key: the browser sends the key for a generation request. Use HTTPS in production. The server does not persist it.
2. Server default key: the deployer sets `DEEPSEEK_API_KEY` or `OPENAI_API_KEY`; the frontend can use AI mode without seeing the key.
3. No key: ExamForge AI falls back to local safe draft mode.

## Render

Create a Docker-based Web Service from this repository. Render will use `Dockerfile`.

Suggested environment:

- `APP_MODE=cloud`
- `DEFAULT_LLM_PROVIDER=deepseek`
- `DEFAULT_LLM_MODEL=deepseek-v4-flash`
- `DEFAULT_LLM_BASE_URL=https://api.deepseek.com`
- `DEEPSEEK_API_KEY=<optional secret>`
- `MAX_UPLOAD_MB=50`
- `LLM_ENABLE_CHUNK_SUMMARY=true`
- `LLM_ENABLE_FINAL_SYNTHESIS=true`

`render.yaml` is included as a starting point.

## Long Material Handling

When uploaded materials exceed the configured context budget, ExamForge AI does not immediately fall back to the local safe draft. It automatically:

1. Splits material by file, page, section, question number, and paragraph boundaries.
2. Builds chunk insights for exam points, definitions, formulas, question patterns, Anki candidates, common mistakes, and evidence snippets.
3. Preserves high-value content such as past-exam questions, formulas, definitions, code, and teacher-emphasized material.
4. Runs final synthesis from the evidence pack, local safe draft, chunk insights, and user settings.
5. Retries with a compact evidence pack if the provider still returns `CONTEXT_TOO_LONG`.

Only after repeated failure does the app return the local safe draft.

## Railway

Railway can build from the root `Dockerfile`.

1. Create a new Railway project from the GitHub repository.
2. Use Dockerfile deployment.
3. Add the environment variables from `.env.example`.
4. Set `DEEPSEEK_API_KEY` only in Railway variables if you want a server default key.

## Fly.io

```bash
fly launch
fly secrets set DEEPSEEK_API_KEY=your_key
fly deploy
```

`fly.toml` is included as a starting point. Review `app` and `primary_region` before deploying.

## Security Notes

- Keep HTTPS enabled in production.
- Restrict `CORS_ORIGINS` to your public domain when cross-origin access is needed.
- Uploads are limited by file count, file size, and extension.
- Executables and archives are rejected by default.
- Runtime directories should not be committed.
- Logs should never include API keys.
