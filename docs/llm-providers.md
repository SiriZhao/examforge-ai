# LLM providers

LLM-first mode is the main semantic generation path. The model interprets course evidence, builds the Course Model and Study Blueprint, writes unit drafts, and synthesizes the canonical study report. Parsing, OCR coordination, source anchors, validation, persistence, retries, and exports remain local backend responsibilities.

## Provider paths

The current UI exposes:

- DeepSeek, with its OpenAI-compatible endpoint defaults.
- OpenAI.
- OpenAI-compatible, for a compatible Base URL and model.

The backend registry also contains Qwen, custom OpenAI-compatible, and mock adapters. A provider should be considered supported for your deployment only after checking its endpoint, model permissions, context limits, CORS behavior, and data policy.

## Configuration fields

- provider
- base_url
- model
- api_key

The model name is user-configured. The repository does not promise that every model at a compatible endpoint has the same context window or output behavior.

## Key handling

The browser saves BYOK configuration in localStorage when the user chooses Save. Generation requests carry the key to the backend; the backend uses it for the selected provider and does not persist it in the workspace database or logs. Never put real keys in .env.example, documentation, screenshots, tests, issues, or commits.

## Request and fallback behavior

The provider layer accepts tolerant JSON/Markdown response forms where the active stage allows it, validates stage output, records diagnostics, and performs bounded repair when appropriate. Timeouts, authentication errors, quota errors, invalid output, or context limits are surfaced as user-facing errors. A complete AI-pipeline failure may enter the explicitly labelled Basic Offline Review fallback; it is not silently presented as an equivalent AI result.

## Adding a provider

Read [CONTRIBUTING.md](../CONTRIBUTING.md). Add tests for request construction, parsing, timeout behavior, key redaction, and fallback behavior. Do not log raw authorization headers or full course material.
