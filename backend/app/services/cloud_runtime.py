from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

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


def frontend_static_dir() -> Path:
    candidates = [
        Path(__file__).resolve().parents[1] / "static",
        Path(__file__).resolve().parents[2] / "static",
        Path(__file__).resolve().parents[3] / "frontend" / "dist",
    ]
    for candidate in candidates:
        if (candidate / "index.html").exists():
            return candidate
    return candidates[0]
