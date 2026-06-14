# ExamForge AI Release Checklist

Use this checklist before making the repository public, pushing a release tag, or publishing a Windows installer.

## 1. Security Check

- [ ] No API keys are committed.
- [ ] No tokens, credentials, cookies, or auth headers are committed.
- [ ] No real user-uploaded files are present.
- [ ] No real course materials, lecture slides, textbooks, past exams, or copyrighted school files are present.
- [ ] No personal local paths, usernames, machine names, or private directories are exposed in docs, configs, logs, or examples.
- [ ] Logs have been cleaned.
- [ ] `.env` files are absent from the repository.
- [ ] Example files only contain fictional demo content.

Suggested commands:

```powershell
git status --short
git grep -n -i "api_key\|apikey\|secret\|token\|password\|authorization\|bearer"
.\scripts\clean-repo.ps1
```

## 2. Repository Check

- [ ] `frontend/node_modules/` is not committed.
- [ ] `backend/.venv/` is not committed.
- [ ] `build/`, `dist/`, `frontend/dist/`, and other build outputs are not committed.
- [ ] `backend/uploads/` contains only `.gitkeep`.
- [ ] `backend/outputs/` contains only `.gitkeep`.
- [ ] `backend/ocr_data/tessdata/` does not contain real `*.traineddata` files unless intentionally distributed.
- [ ] README screenshots and demo GIF placeholders or images render correctly.
- [ ] `LICENSE` exists and matches the README badge.
- [ ] `.gitignore` covers runtime files, logs, local caches, OCR model files, and build outputs.
- [ ] `examples/` contains only fictional, GitHub-safe demo files.

Suggested commands:

```powershell
git status --short
git ls-files frontend/node_modules backend/.venv build dist frontend/dist
git ls-files backend/uploads backend/outputs backend/ocr_data/tessdata
```

## 3. Test Check

- [ ] Backend pytest passes.
- [ ] Frontend vitest passes.
- [ ] Frontend production build passes.
- [ ] Windows `start.bat` starts the local development app successfully.
- [ ] Packaged exe starts successfully.
- [ ] Browser opens to the local app URL.
- [ ] Basic upload and report generation flow works with `examples/` demo files.

Suggested commands:

```powershell
cd backend
.\.venv\Scripts\python.exe -m pytest

cd ..\frontend
npm run test -- --run
npm run build

cd ..
.\scripts\test-all.ps1
```

## 4. Packaging Check

- [ ] `dist/ExamForgeAI.exe` exists.
- [ ] `dist/ExamForgeAI.exe` can start without Python or Node.js installed on the target machine.
- [ ] `dist/installer/ExamForgeAISetup-0.3.2.exe` exists.
- [ ] Installer can install ExamForge AI into the current user's app directory.
- [ ] Installed app starts and opens the browser.
- [ ] Uninstall works normally.
- [ ] Uninstall keeps user data and displays the user data path.
- [ ] Runtime data is written to `%LOCALAPPDATA%/ExamForgeAI`.
- [ ] `uploads`, `outputs`, and `logs` are created under `%LOCALAPPDATA%/ExamForgeAI`.
- [ ] Installation directory is not polluted by uploads, outputs, logs, or caches.

Suggested command:

```powershell
.\scripts\build-windows.ps1
```

Expected outputs:

```text
dist/ExamForgeAI.exe
dist/installer/ExamForgeAISetup-0.3.2.exe
```

## 5. GitHub Release Check

- [ ] Release tag is correct, for example `v0.3.2`.
- [ ] Tag version matches `installer/exam-review-agent.iss`, `installer/version_info.txt`, README, and release notes.
- [ ] Release notes are written and include major changes, known issues, and Windows install instructions.
- [ ] GitHub Actions Windows release workflow completed successfully.
- [ ] `ExamForgeAI.exe` artifact is uploaded.
- [ ] `ExamForgeAISetup-0.3.2.exe` artifact is uploaded.
- [ ] Release assets are attached to the GitHub Release.
- [ ] Download links work from a clean browser session.
- [ ] The release is marked as draft until the installer has been smoke-tested.

Suggested commands:

```powershell
git tag v0.3.2
git push origin v0.3.2
```

After the workflow completes, download the installer from GitHub Releases and run a final clean-machine smoke test.

