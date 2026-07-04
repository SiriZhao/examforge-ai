from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Lock
from uuid import uuid4

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import settings
from app.routers.generate_review import build_generate_review_response
from app.schemas.review import GenerateReviewRequest
from app.services.cloud_runtime import cleanup_runtime_files, runtime_dir
from app.services.text_quality import content_disposition_header

router = APIRouter()

_executor = ThreadPoolExecutor(max_workers=1)
_lock = Lock()
_jobs: dict[str, dict] = {}


@router.post("/generate-review-jobs")
@router.post("/api/review/jobs")
def create_generate_review_job(request: GenerateReviewRequest) -> dict[str, str]:
    cleanup_runtime_files()
    job_id = uuid4().hex
    now = datetime.now().isoformat(timespec="seconds")
    with _lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "status": "pending",
            "progress": 1,
            "message": "Job created. Waiting for processing.",
            "result": None,
            "error": None,
            "created_at": now,
            "updated_at": now,
        }

    _executor.submit(_run_job, job_id, request)
    return {"job_id": job_id}


@router.get("/generate-review-jobs/{job_id}")
@router.get("/api/review/jobs/{job_id}")
def get_generate_review_job(job_id: str) -> dict:
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")
        return job.copy()


@router.get("/api/review/jobs/{job_id}/download/{export_format}")
def download_generate_review_job_file(job_id: str, export_format: str) -> FileResponse:
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found.")
        if job.get("status") != "completed" or not job.get("result"):
            raise HTTPException(status_code=409, detail="Job is not completed.")
        result = job["result"]

    if export_format == "anki":
        download_path = result.get("anki_csv_download_path")
    else:
        download_path = (result.get("download_links") or {}).get(export_format)
    if not download_path:
        raise HTTPException(status_code=404, detail="Requested export is not available.")

    filename = str(download_path).split("/")[-1].split("\\")[-1]
    file_path = (runtime_dir(settings.output_dir) / filename).resolve()
    output_root = runtime_dir(settings.output_dir).resolve()
    try:
        file_path.relative_to(output_root)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid download path.") from exc
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Export file not found.")

    return FileResponse(
        path=file_path,
        filename=filename,
        headers={"Content-Disposition": content_disposition_header(filename)},
    )


def _run_job(job_id: str, request: GenerateReviewRequest) -> None:
    update_job(job_id, status="parsing", progress=3, message="Starting review generation.")

    def progress_callback(progress: int, message: str) -> None:
        update_job(job_id, status=stage_from_progress(progress), progress=progress, message=message)

    try:
        result = build_generate_review_response(request, progress_callback)
        update_job(
            job_id,
            status="completed",
            progress=100,
            message="Completed.",
            result=result.model_dump(mode="json"),
        )
    except HTTPException as exc:
        update_job(job_id, status="failed", progress=100, message="Failed.", error=str(exc.detail))
    except Exception as exc:
        update_job(job_id, status="failed", progress=100, message="Failed.", error=str(exc))


def update_job(
    job_id: str,
    *,
    status: str,
    progress: int,
    message: str,
    result: dict | None = None,
    error: str | None = None,
) -> None:
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job.update(
            {
                "status": status,
                "progress": max(0, min(100, progress)),
                "message": message,
                "updated_at": datetime.now().isoformat(timespec="seconds"),
            }
        )
        if result is not None:
            job["result"] = result
        if error is not None:
            job["error"] = error


def stage_from_progress(progress: int) -> str:
    if progress < 20:
        return "parsing"
    if progress < 60:
        return "ocr"
    if progress < 76:
        return "building_evidence"
    if progress < 86:
        return "llm"
    if progress < 96:
        return "exporting"
    return "validating"
