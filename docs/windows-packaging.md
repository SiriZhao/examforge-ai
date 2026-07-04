# Windows Packaging

This guide explains how to package ExamForge AI as a Windows desktop executable and installer.

The packaged app is designed for ordinary Windows users:

- No Python installation required.
- No Node.js installation required.
- FastAPI runs as an embedded local service.
- The React frontend is served from bundled static files.
- Runtime data is stored under `%LOCALAPPDATA%\ExamForgeAI`.

## Build Locally

Prerequisites for the build machine:

- Windows 10 or newer.
- Python 3.11 or newer.
- Node.js 18 or newer.
- Optional: Inno Setup 6 if you want an installer.

Run from the repository root:

```powershell
.\scripts\build-windows.ps1
```

The script will:

1. Remove old `dist/` and `build/`.
2. Run `npm install`.
3. Run `npm run build` to create `frontend/dist`.
4. Create or reuse `backend/.venv`.
5. Install backend dependencies and PyInstaller.
6. Run backend tests.
7. Run frontend tests.
8. Run `pyinstaller ExamForgeAI.spec`.
9. Build the Inno Setup installer if `ISCC.exe` is available.

Expected outputs:

```text
dist/ExamForgeAI.exe
dist/installer/ExamForgeAISetup-0.4.0.exe
```

If Inno Setup is not installed, the script still produces `dist/ExamForgeAI.exe`.

## Runtime Data

The packaged app does not write uploads, generated reports, or logs into the installation directory.

Runtime data is stored here:

```text
%LOCALAPPDATA%\ExamForgeAI
```

Subdirectories:

- `uploads/`
- `outputs/`
- `logs/`

The main desktop startup log is:

```text
%LOCALAPPDATA%\ExamForgeAI\logs\desktop.log
```

## Release on GitHub

Recommended release checklist:

1. Run the full packaging script:

   ```powershell
   .\scripts\build-windows.ps1
   ```

2. Smoke test `dist/ExamForgeAI.exe` on the build machine.
3. Test the installer `dist/installer/ExamForgeAISetup-0.4.0.exe`.
4. Ideally test on a clean Windows VM without Python and Node.js installed.
5. Create a GitHub Release named `v0.4.0`.
6. Upload:

   ```text
   dist/ExamForgeAI.exe
   dist/installer/ExamForgeAISetup-0.4.0.exe
   ```

7. Include release notes:

   - Local desktop app.
   - No Python or Node.js required for end users.
   - Runtime data path: `%LOCALAPPDATA%\ExamForgeAI`.
   - Known OCR limitations.

## Common Issues

### Windows Defender or SmartScreen warning

Unsigned PyInstaller apps may trigger SmartScreen or antivirus warnings, especially for early open-source releases with low reputation.

Recommended mitigations:

- Publish checksums for release assets.
- Build from a clean CI or clean Windows VM.
- Avoid bundling unrelated files.
- Consider code signing for public releases.

### First startup is slow

The executable may take longer on first launch because PyInstaller extracts bundled files to a temporary directory before starting FastAPI.

This is expected, especially when OCR and ONNX Runtime dependencies are included.

### OCR makes the executable large

OCR dependencies such as `rapidocr_onnxruntime`, `onnxruntime`, `opencv-python`, and model/runtime libraries can significantly increase file size.

Options:

- Keep OCR bundled for one-click usability.
- Offer a smaller "no OCR" build later.
- Download OCR language/model data on first run in a future release.

### Scanned PDF OCR does not work

Scanned PDF OCR may require Poppler and OCR runtime support. The app still works for text PDFs, PPTX, DOCX, Markdown, and images that can be parsed by bundled providers.

Check:

```text
%LOCALAPPDATA%\ExamForgeAI\logs\desktop.log
```

### App starts but browser does not open

Open the log file:

```text
%LOCALAPPDATA%\ExamForgeAI\logs\desktop.log
```

The app writes the local URL it started, usually `http://127.0.0.1:<port>`.

### Port conflict

The desktop app automatically asks the OS for a free local port, so fixed-port conflicts should not block startup.

### Installer uninstall keeps data

Uninstalling ExamForge AI keeps user data by design. Delete this folder manually if needed:

```text
%LOCALAPPDATA%\ExamForgeAI
```


