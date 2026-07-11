# CampusForge v0.5.0

## Major Upgrade

- Rebrands the product layer to CampusForge.
- Adds GitHub Pages frontend deployment workflow.
- Adds Vite base path support for project Pages URLs.
- Adds Supabase and Stripe environment configuration.
- Adds public SaaS configuration and plan catalog endpoints.
- Adds Supabase PostgreSQL/RLS migration baseline.
- Updates Docker, Render and Fly configuration for CampusForge.
- Updates Windows desktop packaging to produce `CampusForge.exe`.

## Reliability

- Keeps long-document chunked LLM processing from v0.5.0.
- Keeps local safe draft fallback for no-key and failed-LLM cases.
- Keeps FastAPI static frontend serving for cloud and desktop modes.

## Required Manual Setup

- Supabase project, Auth URLs, Storage buckets and migration execution.
- Stripe products, prices, Customer Portal and webhook endpoint.
- Public backend deployment URL.
- GitHub Pages variables/secrets.

## Security Notes

- Do not put service role, Stripe secret or AI provider keys in frontend variables or release assets.
- Use HTTPS for browser-provided API keys.
- Enable access controls and rate limits before opening server-funded AI calls publicly.

