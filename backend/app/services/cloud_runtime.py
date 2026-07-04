from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import sys

from app.config import settings


def runtime_dir(path: Path) -> Path:
    if path.is_absolute():
        return path
    return (settings.storage_dir / path).resolve()


def ensure_runtime_directories() -> None:
    for path in [settings.upload_dir, settings.output_dir, settings.ocr_cache_dir]:
        runtime_dir(path).mkdir(parents=True, exist_ok=True)


def cleanup_runtime_files() -> int:
    ttl = timedelta(hours=max(1, settings.temp_file_ttl_hours))
    cutoff = datetime.now() - ttl
    removed = 0
    for root in [runtime_dir(settings.upload_dir), runtime_dir(settings.output_dir), runtime_dir(settings.ocr_cache_dir)]:
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.name == ".gitkeep":
                continue
            try:
                modified = datetime.fromtimestamp(path.stat().st_mtime)
                if modified < cutoff:
                    path.unlink()
                    removed += 1
            except OSError:
                continue
    return removed


def is_storage_writable() -> bool:
    try:
        root = runtime_dir(settings.output_dir)
        root.mkdir(parents=True, exist_ok=True)
        probe = root / ".write_probe"
        probe.write_text("ok", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return True
    except OSError:
        return False


def is_ocr_available() -> bool:
    if not settings.enable_local_ocr:
        return False
    if settings.enable_rapidocr:
        try:
            import rapidocr_onnxruntime  # noqa: F401

            return True
        except Exception:
            pass
    if settings.enable_tesseract:
        try:
            import pytesseract  # noqa: F401

            return True
        except Exception:
            return False
    return False


def is_pyinstaller_bundle() -> bool:
    return bool(getattr(sys, "frozen", False)) and hasattr(sys, "_MEIPASS")


def bundled_base_dir() -> Path | None:
    if is_pyinstaller_bundle():
        return Path(getattr(sys, "_MEIPASS"))
    return None


def frontend_static_candidates() -> list[Path]:
    candidates: list[Path] = []
    bundle_root = bundled_base_dir()
    if bundle_root:
        candidates.extend(
            [
                bundle_root / "frontend" / "dist",
                bundle_root / "frontend_dist",
                bundle_root / "static",
                bundle_root / "web",
            ]
        )

    app_root = Path(__file__).resolve().parents[1]
    backend_root = Path(__file__).resolve().parents[2]
    repo_root = Path(__file__).resolve().parents[3]
    candidates = [
        *candidates,
        app_root / "static",
        backend_root / "static",
        repo_root / "frontend" / "dist",
        repo_root / "backend" / "static",
        repo_root / "static",
    ]
    return candidates


def find_frontend_dist() -> Path | None:
    for candidate in frontend_static_candidates():
        if (candidate / "index.html").exists():
            return candidate
    return None


def frontend_static_dir() -> Path:
    found = find_frontend_dist()
    if found:
        return found
    candidates = frontend_static_candidates()
    return candidates[0]
