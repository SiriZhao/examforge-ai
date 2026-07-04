from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.schemas.review import GenerateReviewResponse, ReviewReport


def test_generate_review_job_status_flow(monkeypatch) -> None:
    def fake_build_generate_review_response(request, progress_callback=None):
        if progress_callback:
            progress_callback(42, "正在测试进度")
        return GenerateReviewResponse(
            review_report=ReviewReport(
                title="测试报告",
                summary="测试总结",
                chapters=[],
                high_frequency_points=[],
                sprint_checklist=[],
                low_priority=[],
                insufficient_materials=[],
                generated_at="2026-06-03T00:00:00",
            ),
            markdown="# 测试报告",
            download_path="/download/test.md",
            download_links={"md": "/download/test.md"},
            export_format="md",
        )

    monkeypatch.setattr(
        "app.routers.generate_review_jobs.build_generate_review_response",
        fake_build_generate_review_response,
    )

    client = TestClient(app)
    response = client.post(
        "/generate-review-jobs",
        json={"files": ["demo.pdf"], "title": "测试报告"},
    )
    assert response.status_code == 200
    job_id = response.json()["job_id"]

    for _ in range(20):
        status_response = client.get(f"/generate-review-jobs/{job_id}")
        assert status_response.status_code == 200
        body = status_response.json()
        if body["status"] == "completed":
            assert body["progress"] == 100
            assert body["result"]["review_report"]["title"] == "测试报告"
            break
    else:
        raise AssertionError("job did not complete")


def test_generate_review_job_api_alias(monkeypatch) -> None:
    def fake_build_generate_review_response(request, progress_callback=None):
        return GenerateReviewResponse(
            review_report=ReviewReport(
                title="Cloud",
                summary="Cloud summary",
                chapters=[],
                high_frequency_points=[],
                sprint_checklist=[],
                low_priority=[],
                insufficient_materials=[],
                generated_at="2026-06-03T00:00:00",
            ),
            markdown="# Cloud",
            download_path="/download/cloud.md",
            download_links={"md": "/download/cloud.md"},
            export_format="md",
        )

    monkeypatch.setattr(
        "app.routers.generate_review_jobs.build_generate_review_response",
        fake_build_generate_review_response,
    )

    client = TestClient(app)
    response = client.post("/api/review/jobs", json={"files": ["demo.pdf"], "title": "Cloud"})
    assert response.status_code == 200
    job_id = response.json()["job_id"]
    status_response = client.get(f"/api/review/jobs/{job_id}")
    assert status_response.status_code == 200
    assert status_response.json()["job_id"] == job_id


def test_cloud_mode_rejects_unscoped_download(tmp_path) -> None:
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    (output_dir / "demo.md").write_text("# demo", encoding="utf-8")
    original_mode = settings.app_mode
    original_output = settings.output_dir
    settings.app_mode = "cloud"
    settings.output_dir = output_dir
    client = TestClient(app)
    try:
        response = client.get("/download/demo.md")
    finally:
        settings.app_mode = original_mode
        settings.output_dir = original_output

    assert response.status_code == 404
    assert "job-scoped" in response.json()["detail"]
