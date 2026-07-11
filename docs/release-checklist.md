# Release Checklist

Use this checklist before publishing a release.

## Build

- `cd frontend && npm install && npm run build && npm run test -- --run`
- `cd backend && python -m pip install -r requirements.txt && python -m pytest`
- `docker build -t examforge-ai:0.5.0 .`
- `.\scripts\build-windows.ps1`

## Security

- Search diffs for `sk-`, `api_key`, `API_KEY`, `Authorization`, `Bearer`, `password`, `secret`, and `token`.
- Confirm `.env`, `.env.local`, `backend/.env`, and `frontend/.env` are not tracked.
- Confirm no real course materials, uploads, generated reports, cache files, or logs are tracked.

## Git Cleanliness

Do not commit:

- `dist/`
- `build/`
- `*.exe`
- `*.msi`
- `*.zip`
- `node_modules/`
- `.venv/`
- `backend/cache/`
- `backend/uploads/`
- `backend/outputs/`

## Release

1. Commit and push source changes.
2. Tag the release, for example `v0.5.0`.
3. Upload `dist/CampusForge.exe` and, if available, `dist/installer/CampusForgeSetup-0.5.0.exe` to GitHub Releases.
4. Do not claim deployment or release success unless the command actually succeeds.
