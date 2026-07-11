# GitHub Pages Deployment

CampusForge uses GitHub Pages only for the static frontend. The FastAPI backend must run on a cloud service such as Render, Railway or Fly.io.

## Enable Pages

1. Open repository Settings.
2. Go to Pages.
3. Set Source to GitHub Actions.
4. Push to `main` or run `Deploy Frontend to GitHub Pages` manually.

## Required Variables

Repository variables:

```text
VITE_API_BASE_URL=https://your-backend.example.com/api
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_or_live_value
```

Repository secrets:

```text
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
```

Do not add service role keys, Stripe secret keys or AI API keys to frontend variables.

## URL Rules

For project repositories, the frontend URL is:

```text
https://<owner>.github.io/<repo>/
```

The Vite base path is computed automatically from `GITHUB_REPOSITORY` unless `VITE_APP_BASE_PATH` is provided.

## SPA Refresh

`frontend/public/404.html` redirects unknown GitHub Pages routes back to `index.html` while preserving path, query string and hash.

## Troubleshooting

- Blank page: check the generated `base` path and browser console.
- API errors: verify `VITE_API_BASE_URL` points to a live HTTPS backend and ends with `/api`.
- Login callback errors: verify Supabase Redirect URLs include the Pages URL.
- Stale chunks: hard refresh or clear Pages cache by redeploying.

