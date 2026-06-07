from pathlib import Path

from app.config import settings


class UploadResolveError(RuntimeError):
    pass


class UploadedFileNotFoundError(UploadResolveError):
    pass


def resolve_uploaded_file(file_ref: str) -> Path:
    upload_root = settings.upload_dir.resolve()
    candidate = Path(file_ref)
    if not candidate.is_absolute():
        candidate = settings.upload_dir / candidate

    resolved = candidate.resolve()
    try:
        resolved.relative_to(upload_root)
    except ValueError as exc:
        raise UploadResolveError(
            "只能解析上传目录中的文件。"
        ) from exc

    if not resolved.exists():
        raise UploadedFileNotFoundError(f"上传文件不存在：{file_ref}。")

    return resolved
