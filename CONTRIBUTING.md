# Contributing

Thanks for helping improve CampusForge.

## Development

```powershell
cd backend
python -m pytest

cd ../frontend
npm run build
```

## Security

- Never commit API keys, tokens, cookies, or private course materials.
- Do not add logs that print request bodies containing API keys.
- Use `.env.example` only for placeholder configuration.

## Pull Requests

- Keep changes focused.
- Add or update tests when behavior changes.
- Mention any OCR, PDF, or system dependency impact.

## Adding an OCR Provider

1. Create a file under `backend/app/services/ocr_providers/`.
2. Subclass `BaseOCRProvider`.
3. Register it in `ocr_providers/registry.py`.
4. Add mock tests. Never hard-code API keys.

## Adding an LLM Provider

1. Create a file under `backend/app/services/llm_providers/`.
2. Subclass `BaseLLMProvider`.
3. Register it in `llm_providers/registry.py`.
4. Ensure JSON parsing fallback returns the rule-based report when enhancement fails.
