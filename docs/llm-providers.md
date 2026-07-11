# LLM Providers

CampusForge works without an LLM by generating a local safe draft. Optional LLM enhancement can improve topic naming, question type inference, mock exams, Anki cards, and sprint plans.

## Supported Configuration

The current provider path is OpenAI-compatible chat completions, including DeepSeek-compatible endpoints.

Common fields:

- `provider`
- `base_url`
- `model`
- `api_key`

Server-side defaults can be configured with environment variables such as `DEFAULT_LLM_PROVIDER`, `DEFAULT_LLM_MODEL`, `DEFAULT_LLM_BASE_URL`, `DEEPSEEK_API_KEY`, and `OPENAI_API_KEY`.

User-provided keys should be used for the current request and should not be persisted by the server.

## Output Handling

LLM output is treated as untrusted and may be:

- JSON
- JSON inside a Markdown code fence
- JSON with explanatory text around it
- full Markdown

The backend parses these formats tolerantly, validates quality, attempts one repair when useful, and falls back to `local_safe_draft` when the LLM result is not usable.

## Provider Guidelines

When adding a provider:

1. Add the provider under `backend/app/services/llm_providers/`.
2. Register it in the provider registry.
3. Never log raw API keys or authorization headers.
4. Add tests for parsing, timeout behavior, fallback behavior, and key redaction.
5. Keep the local safe draft path working when the provider fails.
