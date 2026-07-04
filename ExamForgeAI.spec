# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

from PyInstaller.utils.hooks import collect_all, collect_submodules


root = Path.cwd()
frontend_dist = root / "frontend" / "dist"
if not (frontend_dist / "index.html").exists():
    raise SystemExit("frontend/dist/index.html was not found. Run npm run build before PyInstaller.")

datas = [
    (str(frontend_dist), "frontend/dist"),
    (str(root / "backend" / "app"), "app"),
]
binaries = []
hiddenimports = [
    "app.main",
    "app.routers.analyze",
    "app.routers.chat",
    "app.routers.download",
    "app.routers.export",
    "app.routers.generate_review",
    "app.routers.generate_review_jobs",
    "app.routers.mock_exam",
    "app.routers.parse",
    "app.routers.upload",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
]

for package_name in [
    "rapidocr_onnxruntime",
    "onnxruntime",
    "cv2",
    "numpy",
    "PIL",
    "pytesseract",
    "pdf2image",
    "pypdf",
    "docx",
    "pptx",
    "markdown",
    "reportlab",
    "weasyprint",
    "pydantic_settings",
]:
    package_datas, package_binaries, package_hiddenimports = collect_all(package_name)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hiddenimports

hiddenimports += collect_submodules("multipart")

excludes = [
    "pytest",
    "unittest",
    "tkinter",
    "frontend",
    "node_modules",
    "tests",
]


a = Analysis(
    ["desktop_main.py"],
    pathex=[str(root / "backend"), str(root)],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="ExamForgeAI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="installer/examforge.ico",
    version="installer/version_info.txt",
)
