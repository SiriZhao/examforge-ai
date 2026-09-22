# Contributing to RecallForge AI

Thanks for helping improve RecallForge AI. Contributions are welcome in documentation, parsers, OCR adapters, LLM provider adapters, exports, tests, evaluation fixtures, accessibility, UI/UX, and internationalization.

## Before you start

Please search existing issues and read the relevant guide in [docs/](docs/README.md). For a security vulnerability, do not open a public issue; follow [SECURITY.md](SECURITY.md).

## Development setup

Requirements: Python 3.11+, Node.js 20+, and npm. Docker, Tesseract, RapidOCR, Inno Setup, and PyInstaller are optional for platform-specific work.

Run the backend and frontend as described in the [README Quick Start](README.md#quick-start). Keep API keys, user uploads, databases, caches, generated exports, dist, build, virtual environments, and node_modules out of commits.

## Repository layout

- backend/: FastAPI API, parsing/OCR, generation pipeline, storage, exports, and Python tests.
- frontend/: React/Vite workspace, report views, and Vitest tests.
- docs/: user, architecture, provider, deployment, and privacy guides.
- examples/: fictional demo materials only.
- .github/: CI, release automation, issue templates, and pull-request guidance.

## Branches and changes

Create a focused branch from main, for example docs/improve-provider-guide or fix/parser-warning. Keep unrelated refactors out of a documentation or bug-fix PR. Do not rewrite release tags or force-push shared branches.

For documentation changes, verify every command, link, image, provider claim, and compatibility note against the current code. If you find a product bug while documenting a flow, record it in the PR or an issue rather than expanding scope silently.

## Tests and checks

From the repository root, run the backend tests and then the frontend checks:

    python -m pytest backend
    cd frontend
    npm ci
    npm run test -- --run
    npm run lint
    npm run typecheck
    npm run build

Run the smallest relevant checks while iterating, then run the full applicable set before opening a PR. Windows packaging changes should also be checked with scripts/build-windows.ps1 when the required tools are available.

## Adding an LLM provider

1. Add the adapter under backend/app/services/llm_providers/.
2. Register it in the provider registry and update the provider documentation.
3. Keep API keys and authorization headers out of logs and errors.
4. Test request construction, response parsing, timeout behavior, redaction, and explicit offline fallback.
5. Do not describe a provider as first-class support unless the repository actually tests and documents that path.

## Adding an OCR provider

1. Add an implementation under backend/app/services/ocr_providers/.
2. Register it in the OCR registry.
3. Preserve text-layer skipping, cache behavior, partial-page failure handling, and source anchors.
4. Add tests and document optional dependencies and configuration.

## Pull requests

A good PR explains the problem, user impact, approach, and verification. UI changes should include a screenshot from the real application. Documentation changes should mention the pages and commands checked.

Use the pull-request template and confirm:

- Tests or checks are listed.
- No API keys, tokens, private course materials, databases, uploads, or caches are included.
- Privacy and security implications are described.
- User-facing behavior and documentation are consistent.
- Compatibility identifiers are preserved unless a deliberate migration is included.

## Issue reports

Use the templates for bugs, features, and documentation corrections. Include version, OS, installation method, reproducible steps, expected behavior, actual behavior, and sanitized logs where relevant. Never paste API keys or private course materials.

## Commits and code style

Use concise, imperative commit messages such as docs: clarify LLM key storage or fix: preserve OCR source anchors. Keep commits reviewable; do not squash or rewrite other contributors' history. Prefer small, typed, testable changes and keep parsing, validation, persistence, and export responsibilities explicit.

Thank you for improving clarity, reliability, accessibility, and reproducibility for RecallForge AI users.
