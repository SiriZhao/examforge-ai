# Security Notes

ExamForge AI handles uploaded learning materials, generated reports, and optional LLM API credentials. Treat public deployments as data-processing services.

## Secrets

- Do not commit `.env`, API keys, tokens, cookies, or private credentials.
- Use `.env.example` only as a placeholder reference.
- In cloud deployments, configure server-side keys through the hosting provider's secret manager.
- Health endpoints must only expose whether an LLM provider is configured, not the key itself.

## Uploads

- Only allow supported document and image types.
- Reject executable files, scripts, archives, and unknown extensions.
- Sanitize filenames before saving.
- Keep uploads inside the configured upload directory.
- Do not expose server paths in user-facing errors.

## Downloads

- Cloud downloads should use job-scoped URLs.
- Do not let users pass arbitrary filesystem paths.
- Use safe `Content-Disposition` filenames for exported files.

## Logging

- Do not log API keys, authorization headers, full uploaded documents, full generated reports, cookies, sessions, or environment variables.
- If debugging LLM responses, log only a short preview and redact likely secrets.

## Public Deployments

Before opening a public instance, add or configure:

- HTTPS
- access control or login
- rate limiting
- file size limits
- job timeouts
- temporary file cleanup
- API cost monitoring
- abuse prevention

## Local Desktop Use

The Windows desktop app is the safer choice for private or institution-restricted materials because files stay on the user's machine unless the user enables an external LLM provider.
