# CampusForge v0.5.0 Audit Report

## 1. Current Architecture

- Frontend: React, Vite, TypeScript, Vitest.
- Backend: FastAPI, Pydantic Settings, local file storage, OCR/document parsing, LLM providers.
- Desktop: PyInstaller one-file Windows client that starts the FastAPI app and opens the browser.
- Cloud: Dockerfile runs FastAPI and serves the built frontend.
- CI/CD: Windows release workflow existed; v0.5.0 adds GitHub Pages frontend deployment workflow.

## 2. Current Working Features

- File upload for PDF, PPTX, DOCX, Markdown, TXT and images.
- OCR fallback and local cache.
- Evidence pack, local safe draft, tolerant LLM parsing, chunked LLM synthesis.
- Markdown, DOCX, PDF and Anki CSV export.
- Job-based generation endpoints.
- Static frontend serving from FastAPI in cloud and PyInstaller modes.

## 3. Missing SaaS Features Before v0.5.0

- No production user registration/login flow.
- No Supabase Auth integration in frontend.
- No server-side JWT verification for private APIs.
- No Stripe Checkout, Customer Portal or webhook implementation.
- No credit reservation/consumption transaction logic.
- No administrator dashboard.
- No deployed public backend URL in this local environment.

## 4. v0.5.0 Implemented Baseline

- Product metadata updated to CampusForge v0.5.0.
- GitHub Pages base path support added to Vite.
- GitHub Pages workflow added.
- Supabase/Stripe environment variables added.
- Public SaaS configuration route added at `/api/saas/config`.
- Public plan catalog route added at `/api/saas/plans`.
- Health check now exposes only boolean provider status, not secrets.
- Supabase migration with RLS baseline added.
- Manual action documentation added.

## 5. Security Risks

- Production auth is not complete until Supabase JWT validation is wired to private endpoints.
- Billing is not complete until Stripe webhooks are verified server-side and credit mutations are transactional.
- Public GitHub Pages frontend must never contain service role, Stripe secret or AI provider keys.
- Uploaded files and generated reports remain sensitive user data; cloud operators need retention, deletion and access policies.

## 6. API Key Leakage Risk

- `.env` and `.env.*` are ignored except `.env.example`.
- `.env.example` contains placeholders only.
- Server keys are read from environment variables.
- `/api/health` and `/api/saas/config` return booleans only for secret-backed services.

## 7. User Data Isolation Risk

- Existing local generation endpoints are not yet user-scoped.
- Supabase migration defines owner-scoped tables and RLS policies.
- Backend still needs enforced JWT authentication before multi-user production use.

## 8. Payment Risk

- Stripe keys and webhook secret are configurable.
- Payment event tables are present in migration.
- Checkout, portal, webhook verification and idempotent credit mutation are not yet implemented.

## 9. Cost Control Risk

- Upload limits, job timeout and chunking budgets exist.
- Server-default LLM keys require deployment-level rate limiting before public launch.
- Credit enforcement is not active until billing and usage middleware are implemented.

## 10. Build and Deployment Blockers

- GitHub CLI was available previously but not authenticated in this local environment.
- Render CLI/API key availability must be checked during release.
- Docker is required to verify image build locally.
- Supabase and Stripe require account-level setup outside this repository.

## 11. Files to Keep

- `backend/`, `frontend/`, `scripts/`, `installer/`, `docs/`, `supabase/`.
- `Dockerfile`, `render.yaml`, `fly.toml`, `.github/workflows/*`.
- `CampusForge.spec` is the PyInstaller build spec and produces `CampusForge.exe`.

## 12. Files Not to Commit

- `dist/`, `build/`, `*.exe`, `*.msi`, `*.zip`.
- `node_modules/`, `.venv/`, `backend/cache/`, `backend/uploads/`, `backend/outputs/`.
- Real course materials, generated reports, `.env` and API keys.

## 13. v0.5.0 Implementation Plan

1. Finish Supabase Auth frontend integration.
2. Add backend JWT verification dependency and protect private endpoints.
3. Move cloud files to Supabase Storage by owner/project path.
4. Add Stripe Checkout, Portal and Webhook routes.
5. Implement credit reservation, consumption and refunds as database transactions.
6. Add admin-only APIs and dashboard.
7. Add end-to-end tests for cross-user isolation.
8. Deploy backend to Render/Railway/Fly.
9. Configure GitHub Pages to call the deployed backend.

