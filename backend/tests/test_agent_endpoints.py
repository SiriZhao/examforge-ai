from fastapi.testclient import TestClient

from app.main import app


def test_generic_chat_route_is_not_part_of_focused_product() -> None:
    client = TestClient(app)
    assert client.post("/chat", json={}).status_code in {404, 405}


def test_review_health_is_available_without_login() -> None:
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
