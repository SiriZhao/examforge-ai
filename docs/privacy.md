# Privacy Notice

ExamForge AI can run as a local desktop app or as a cloud web app. Privacy expectations differ by deployment mode.

## Cloud Deployments

- Uploaded files are processed by the server that hosts ExamForge AI.
- Generated reports, exports, OCR cache, and temporary files are stored in the configured runtime directories until cleanup.
- If the deployer configures a server-side LLM API key, selected material evidence may be sent to the configured LLM provider.
- If a user provides their own API key, the backend uses it for the current request and does not intentionally persist it on the server.
- Production deployments should use HTTPS before accepting user-provided API keys.

## Desktop Deployments

The Windows desktop build is better for sensitive materials because uploads, exports, logs, and caches stay on the user's machine.

## User Responsibility

Do not upload materials you are not authorized to process, redistribute, or send to third-party APIs. Avoid uploading files containing personal data, private exam content, or institution-restricted materials unless you have permission.

Deployers are responsible for complying with applicable laws, school or organization rules, and third-party API terms.
