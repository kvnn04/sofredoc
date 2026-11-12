"""Smoke MOD-00: la app se importa y `/api/v1/health` responde correctamente."""

from fastapi.testclient import TestClient

from src.main import API_VERSION, create_app


def test_health_responde_ok() -> None:
    """CU-02: `GET /api/v1/health` → 200 con status ok, versión y modo extractor."""
    client = TestClient(create_app())

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == API_VERSION
    assert body["extractor_mode"] in ("mock", "llm")
