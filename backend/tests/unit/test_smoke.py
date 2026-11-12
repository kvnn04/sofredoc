"""Smoke MOD-00: la app se importa y `/api/v1/health` responde correctamente."""

from fastapi.testclient import TestClient

from src.config import Settings
from src.main import API_VERSION, create_app


def test_health_responde_ok(tmp_path) -> None:
    """CU-02: `GET /api/v1/health` → 200 con status ok, versión y modo extractor."""
    settings = Settings(db_path=str(tmp_path / "smoke.db"), extractor_mode="mock")
    # `with` ejecuta el lifespan: cierra la conexión SQLite al salir (sin ResourceWarning).
    with TestClient(create_app(settings=settings)) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["version"] == API_VERSION
    assert body["extractor_mode"] == "mock"
