"""App factory del backend SofreDoc Validator (FastAPI monolito)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import get_settings

API_VERSION = "0.1.0"


def create_app() -> FastAPI:
    """Crea la aplicación FastAPI: CORS + endpoint de salud.

    Los routers de `presentation/routers/` se registran aquí a partir de MOD-03.
    """
    app = FastAPI(title="SofreDoc Validator API", version=API_VERSION)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=get_settings().cors_origins_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/api/v1/health")
    def health() -> dict[str, str]:
        """CU-02: verificación de salud del servicio."""
        current = get_settings()
        return {
            "status": "ok",
            "version": API_VERSION,
            "extractor_mode": current.extractor_mode,
        }

    return app


app = create_app()
