from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def workspace_headers(client: TestClient) -> dict[str, str]:
    response = client.post("/api/review-projects/workspace", json={"workspace_id": str(uuid4())})
    assert response.status_code == 201
    body = response.json()
    return {"X-Workspace-Id": body["workspace_id"], "X-Workspace-Secret": body["workspace_secret"]}


def test_workspace_secret_is_required_and_isolates_projects() -> None:
    with TestClient(app) as client:
        first = workspace_headers(client)
        second = workspace_headers(client)
        project = client.post("/api/review-projects/projects", headers=first, json={"course_name": "概率论"})
        assert project.status_code == 201
        assert client.get("/api/review-projects/projects", headers=second).json() == []
        assert client.get("/api/review-projects/projects").status_code == 401


def test_project_upload_and_diagnosis_use_owned_materials() -> None:
    with TestClient(app) as client:
        headers = workspace_headers(client)
        project_id = client.post("/api/review-projects/projects", headers=headers, json={"course_name": "植物学"}).json()["id"]
        upload = client.post(
            f"/api/review-projects/projects/{project_id}/upload",
            headers=headers,
            files={"files": ("2025期末试卷.txt", "名词解释：叶绿体。请说明光合作用。", "text/plain")},
        )
        assert upload.status_code == 201
        diagnosis = client.get(f"/api/review-projects/projects/{project_id}/diagnosis", headers=headers)
        assert diagnosis.status_code == 200
        assert diagnosis.json()["has_past_exams"] is True


def test_report_modules_have_stable_ids_and_versions() -> None:
    with TestClient(app) as client:
        headers = workspace_headers(client)
        project_id = client.post("/api/review-projects/projects", headers=headers, json={"course_name": "高等数学"}).json()["id"]
        report = client.post(f"/api/review-projects/projects/{project_id}/reports", headers=headers).json()
        modules = client.get(f"/api/review-projects/reports/{report['report_id']}/modules", headers=headers).json()
        assert len(modules) == 9
        update = client.put(f"/api/review-projects/reports/{report['report_id']}/modules/{modules[0]['id']}", headers=headers, json={"content": {"title": "考试概览"}, "change_summary": "local edit"})
        assert update.status_code == 200
        assert update.json()["version"] == 1
