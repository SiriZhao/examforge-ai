# LLM Providers

Current production path is rule-based MVP generation. The request accepts LLM configuration so provider support can be added without changing the frontend flow.

Planned providers:

- `mock`
- `openai`
- `custom_openai_compatible`
- `deepseek`
- `qwen`

No API key is required for rule-based generation.

## Add a Provider

Add a new provider under `backend/app/services/llm_providers/`, subclass `BaseLLMProvider`, then register it in `registry.py`. Providers should return a valid `ReviewReport`; if parsing or validation fails, fallback to the rule-based report and mark the uncertainty.
