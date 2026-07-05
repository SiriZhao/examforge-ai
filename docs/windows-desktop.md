# Windows Desktop Build

The desktop edition packages the FastAPI backend and built frontend into a Windows executable.

## Build

Run from the repository root:

```powershell
.\scripts\build-windows.ps1
```

The script should:

1. Stop old ExamForge AI processes.
2. Remove old `dist/` and `build/` outputs.
3. Build `frontend/dist`.
4. Run PyInstaller with `ExamForgeAI.spec`.
5. Include `frontend/dist` in the packaged executable.
6. Produce `dist/ExamForgeAI.exe`.
7. Produce `dist/installer/ExamForgeAISetup-0.4.1.exe` when Inno Setup is available.

## Verify

Start:

```powershell
.\dist\ExamForgeAI.exe
```

Then check:

- The browser opens ExamForge AI.
- `/api/health` returns JSON with version and mode.
- The page does not show `Frontend build not found`.
- A small file can be uploaded and exported.

Do not commit `dist/`, `build/`, or executable files to the main branch. Upload them only to GitHub Releases.
