from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_rejects_non_japanese_input() -> None:
    client = TestClient(app)
    response = client.post("/api/word/analyze", json={"word": "hashi"})
    assert response.status_code == 200
    body = response.json()
    assert body["validation"]["is_valid"] is False
    assert body["directed_prompts"] == []
