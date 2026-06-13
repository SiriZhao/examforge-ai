import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from app.config import settings
from app.schemas.review import OCRConfig, ParsedPage


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def cache_key(path: Path, config: OCRConfig) -> str:
    material = {
        "file_hash": file_hash(path),
        "provider": config.provider,
        "language": config.language,
        "mode": config.mode,
    }
    return hashlib.sha256(json.dumps(material, sort_keys=True).encode("utf-8")).hexdigest()


def cache_path(path: Path, config: OCRConfig) -> Path:
    return settings.ocr_cache_dir / f"{cache_key(path, config)}.json"


def load_ocr_cache(path: Path, config: OCRConfig) -> list[ParsedPage] | None:
    target = cache_path(path, config)
    if not target.exists():
        return None
    try:
        data = json.loads(target.read_text(encoding="utf-8"))
        return [ParsedPage.model_validate(page) for page in data.get("pages", [])]
    except Exception:
        return None


def save_ocr_cache(
    path: Path,
    config: OCRConfig,
    pages: list[ParsedPage],
    *,
    page_count: int,
) -> None:
    settings.ocr_cache_dir.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {
        "file_hash": file_hash(path),
        "ocr_provider": config.provider,
        "ocr_mode": config.mode,
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "page_count": page_count,
        "extracted_text": "\n\n".join(page.text for page in pages if page.text.strip()),
        "per_page_text": [page.text for page in pages],
        "pages": [page.model_dump() for page in pages],
    }
    cache_path(path, config).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
