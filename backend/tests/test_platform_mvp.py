from fastapi.testclient import TestClient
from app.main import app


def test_local_workspace_requires_no_account() -> None:
    with TestClient(app) as client:
        info = client.get("/api/v1/workspace")
        assert info.status_code == 200
        assert info.json()["mode"] == "local"
        assert info.json()["api_key_persistence"] == "browser_only"
        assert client.get("/api/v1/courses").status_code == 200
        assert client.post("/api/v1/auth/login", json={}).status_code in {404, 405}


def test_course_file_creates_real_citations() -> None:
    with TestClient(app) as client:
        course_id = client.post("/api/v1/courses", json={"name": "植物学"}).json()["id"]
        upload = client.post(f"/api/v1/courses/{course_id}/files", files={"uploaded": ("notes.txt", "光合作用将光能转化为化学能。叶绿体是重要场所。", "text/plain")})
        assert upload.status_code == 201
        result = client.post(f"/api/v1/courses/{course_id}/search", json={"query": "光合作用"})
        assert result.status_code == 200
        assert result.json()["citations"][0]["file_name"] == "notes.txt"
        assert result.json()["citations"][0]["chunk_id"]


def test_missing_model_is_a_product_message_not_an_error() -> None:
    with TestClient(app) as client:
        conversation = client.post("/api/v1/conversations", json={"title": "学习"}).json()
        response = client.post(f"/api/v1/conversations/{conversation['id']}/messages", json={"content": "解释概率"})
        assert response.status_code == 201
        assert response.json()["needs_model_config"] is True
        assert "尚未配置AI模型" in response.json()["reply"]["content"]
