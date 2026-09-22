# Security policy

## Supported versions

The latest main branch and latest published release receive security attention. RecallForge AI is a v0.x project, so security behavior may evolve between releases.

## Reporting a vulnerability

Do not disclose credentials, exploit details, private course materials, database files, or user uploads in a public issue. If GitHub private vulnerability reporting is enabled for this repository, use that channel. Otherwise, contact the maintainers through a private GitHub communication with the minimum reproducible details.

Please include the affected version or commit, component, impact, prerequisites, safe reproduction steps, and a suggested mitigation when known.

## Secrets and private materials

- Never commit API keys, access tokens, cookies, .env files, or credentials.
- Never attach private course material, workspace.db, uploads, caches, or generated user reports to public issues or pull requests.
- Redact authorization headers and request bodies before sharing logs.
- Treat model providers as external recipients whenever a request sends course material outside the local process.

## Disclosure

We will acknowledge a valid report, investigate it, and coordinate a fix or mitigation before public disclosure when practical. Please avoid testing against other users, shared deployments, or systems you do not own.
