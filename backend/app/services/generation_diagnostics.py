from __future__ import annotations

import logging
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Any

from app.config import settings


logger = logging.getLogger("recallforge.generation")
_diagnostic_context: ContextVar[dict[str, Any]] = ContextVar(
    "recallforge_generation_diagnostic_context",
    default={},
)
_SENSITIVE_KEYS = {
    "api_key",
    "authorization",
    "prompt",
    "materials_text",
    "response",
    "content",
    "chapter_text",
    "chunk_text",
}


@contextmanager
def diagnostic_context(**metadata: Any):
    """Attach correlation metadata to provider-level diagnostics in this call context."""
    token = _diagnostic_context.set({**_diagnostic_context.get(), **metadata})
    try:
        yield
    finally:
        _diagnostic_context.reset(token)


def diagnostic(event: str, **metadata: Any) -> None:
    if settings.environment.lower() not in {"development", "dev", "test", "local"} and settings.app_mode != "local_dev":
        return
    safe = _sanitize_metadata({**_diagnostic_context.get(), **metadata})
    logger.info("generation_event=%s metadata=%s", event, safe)


def _sanitize_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    safe: dict[str, Any] = {}
    for key, value in metadata.items():
        if key.lower() in _SENSITIVE_KEYS:
            continue
        if isinstance(value, dict):
            safe[key] = _sanitize_metadata(value)
        elif isinstance(value, (list, tuple)):
            safe[key] = [
                item[:500] if isinstance(item, str) else item
                for item in value[:50]
            ]
        elif isinstance(value, str):
            safe[key] = value[:500]
        else:
            safe[key] = value
    return safe
