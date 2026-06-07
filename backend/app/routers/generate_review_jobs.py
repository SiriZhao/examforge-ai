from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from threading import Lock
from uuid import uuid4

from fastapi import APIRouter, HTTPException

from app.routers.generate_review import build_generate_review_response
from app.schemas.review import GenerateReviewRequest

router = APIRouter()

_executor = ThreadPoolExecutor(max_workers=1)
_lock = Lock()
_jobs: dict[str, dict] = {}


@router.post("/generate-review-jobs")
def create_generate_review_job(request: GenerateReviewRequest) -> dict[str, str]:
    job_id = uuid4().hex
    now = datetime.now().isoformat(timespec="seconds")
    with _lock:
        _jobs[job_id] = {
            "job_id": job_id,
            "status": "queued",
            "progress": 1,
            "message": "任务已创建，正在排队。",
            "result": None,
            "error": None,
            "created_at": now,
            "updated_at": now,
        }

    _executor.submit(_run_job, job_id, request)
    return {"job_id": job_id}


@router.get("/generate-review-jobs/{job_id}")
def get_generate_review_job(job_id: str) -> dict:
    with _lock:
        job = _jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="生成任务不存在。")
        return job.copy()


def _run_job(job_id: str, request: GenerateReviewRequest) -> None:
    update_job(job_id, status="running", progress=3, message="正在启动生成流程。")

    def progress_callback(progress: int, message: str) -> None:
        update_job(job_id, status="running", progress=progress, message=message)

    try:
        result = build_generate_review_response(request, progress_callback)
        update_job(
            job_id,
            status="completed",
            progress=100,
            message="已完成。",
            result=result.model_dump(mode="json"),
        )
    except HTTPException as exc:
        update_job(
            job_id,
            status="failed",
            progress=100,
            message="生成失败。",
            error=str(exc.detail),
        )
    except Exception as exc:
        update_job(
            job_id,
            status="failed",
            progress=100,
            message="生成失败。",
            error=str(exc),
        )


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
