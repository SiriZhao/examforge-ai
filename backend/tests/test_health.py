from fastapi.testclient import TestClient

from app.main import app


def test_health_check() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == "0.5.1"
    assert body["mode"] in {"local_dev", "desktop", "cloud"}
    assert "llm_server_configured" in body
    assert "llm_provider_configured" in body
    assert "ocr_available" in body
    assert "storage_writable" in body


def test_api_health_does_not_expose_llm_key() -> None:
    client = TestClient(app)
    response = client.get("/api/health")

    assert response.status_code == 200
    body = response.json()
    assert "api_key" not in body
    assert "DEEPSEEK_API_KEY" not in str(body)
