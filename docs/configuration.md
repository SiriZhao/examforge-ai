# Configuration

RecallForge AI has two configuration surfaces: browser-side BYOK settings and optional server/runtime environment settings.

## Browser BYOK settings

The model settings dialog accepts provider, Base URL, model name, and API key. When saved, this configuration is stored in the current browser's localStorage under a legacy compatibility key. It is not written to the workspace database or application logs. The key is sent with generation requests to the backend, which uses it for the selected provider.

Use a private browser profile for sensitive keys. Delete the site's browser data to remove the saved configuration.

## Server environment

Copy .env.example as a reference and keep real .env files out of Git. Useful settings include APP_MODE, APP_VERSION, CORS_ORIGINS, STORAGE_DIR, UPLOAD_DIR, OUTPUT_DIR, OCR_CACHE_DIR, upload limits, timeout values, ENABLE_LOCAL_OCR, ENABLE_RAPIDOCR, ENABLE_TESSERACT, DEFAULT_LLM_PROVIDER, DEFAULT_LLM_MODEL, DEFAULT_LLM_BASE_URL, and ENABLE_SERVER_LLM_KEY.

Server-side provider keys can be configured for a deployment, but a public service should not silently expose a shared developer key. Review cloud deployment and privacy guidance before enabling it.

## Modes

- local_dev: Vite frontend with a local FastAPI backend.
- desktop: packaged Windows app with local runtime data.
- cloud: Docker-hosted service with anonymous workspace isolation and configured temporary-file cleanup.

See [API configuration](api-configuration.md), [LLM providers](llm-providers.md), and [deployment modes](deployment.md).
