# Manual Actions Required for CampusForge v0.5.0

These actions require account owner access or third-party credentials. They were not executed automatically in the local coding environment.

## GitHub

1. Confirm whether the repository should remain `SiriZhao/campusforge` or be renamed to `campusforge`.
2. Settings -> Pages -> Source: select GitHub Actions.
3. Add repository variables:
   - `VITE_API_BASE_URL`
   - `VITE_SUPABASE_URL`
   - `VITE_STRIPE_PUBLISHABLE_KEY`
4. Add repository secret:
   - `VITE_SUPABASE_ANON_KEY`
5. If GitHub CLI is not authenticated, create Release `v0.5.0` manually and upload:
   - `dist/CampusForge.exe`
   - `dist/installer/CampusForgeSetup-0.5.0.exe` if present

## Supabase

1. Create a Supabase project.
2. Run `supabase/migrations/0001_campusforge_saas.sql` in a staging project first.
3. Configure Auth Site URL to the GitHub Pages URL.
4. Add redirect URLs for:
   - `https://<owner>.github.io/<repo>/auth/callback`
   - `https://<owner>.github.io/<repo>/reset-password`
   - `http://localhost:5173/auth/callback`
   - `http://localhost:5173/reset-password`
5. Create Storage buckets for user uploads and generated exports.
6. Keep `SUPABASE_SERVICE_ROLE_KEY` only in the backend environment.

## Stripe

1. Create Products and Prices for Free, Student Plus and credit packs.
2. Configure Checkout and Customer Portal.
3. Add webhook endpoint on the deployed backend.
4. Store only these backend environment variables:
   - `STRIPE_SECRET_KEY`
   - `STRIPE_WEBHOOK_SECRET`
   - `STRIPE_PUBLISHABLE_KEY`
5. Verify webhook signatures before processing payments.

## Cloud Backend

1. Deploy Docker service to Render, Railway or Fly.io.
2. Set `APP_MODE=cloud`.
3. Set `PUBLIC_BASE_URL` to the public backend URL.
4. Configure `CORS_ORIGINS` to the GitHub Pages URL and local dev URLs.
5. Configure AI provider keys only if the operator wants server-funded AI calls.
6. Verify `/api/health` and `/api/saas/config`.

