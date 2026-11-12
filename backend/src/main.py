"""App factory del backend SofreDoc Validator (FastAPI monolito, MOD-03)."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.application.auditar_comprobante import AuditarComprobanteUseCase
from src.config import Settings, get_settings
from src.domain.ports.clock_port import ClockPort
from src.domain.ports.document_extractor_port import DocumentExtractorPort
from src.infrastructure.clock import RelojSistema
from src.infrastructure.db.sqlite_repository import SqliteAuditoriaRepository
from src.infrastructure.llm.factory import crear_extractor
from src.infrastructure.padron.json_padron import JsonPadronProveedores
from src.infrastructure.pdf.pypdf_adapter import PypdfTextExtractor
from src.presentation.errores import registrar_handlers
from src.presentation.routers import auditar, ejemplos, historial

API_VERSION = "0.1.0"

_RUTA_BACKEND = Path(__file__).resolve().parent.parent  # backend/


def create_app(
    settings: Settings | None = None,
    *,
    extractor: DocumentExtractorPort | None = None,
    reloj: ClockPort | None = None,
) -> FastAPI:
    """Crea la app: CORS + health + routers con la infraestructura inyectada.

    Crea las tablas SQLite al arranque (T-11) y arma el caso de uso con los
    adaptadores de `infrastructure/` según `EXTRACTOR_MODE`. Los parámetros
    opcionales `extractor`/`reloj` permiten reemplazar adaptadores en pruebas
    (stub que falla, reloj fijo); por defecto se construyen según settings.
    """
    config = settings or get_settings()
    repo = SqliteAuditoriaRepository(config.resolve_path(config.db_path))

    @asynccontextmanager
    async def _apagar(app: FastAPI) -> AsyncIterator[None]:
        yield
        repo.cerrar()

    app = FastAPI(title="SofreDoc Validator API", version=API_VERSION, lifespan=_apagar)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins_list,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    use_case = AuditarComprobanteUseCase(
        pdf_port=PypdfTextExtractor(),
        extractor=extractor or crear_extractor(config),
        padron=JsonPadronProveedores(config.resolve_path(config.padron_path)),
        clock=reloj or RelojSistema(),
        repo=repo,
    )
    app.state.settings = config
    app.state.auditar_use_case = use_case
    app.state.auditorias_repo = repo
    app.state.directorio_ejemplos = _RUTA_BACKEND / "data" / "ejemplos"

    registrar_handlers(app)
    app.include_router(auditar.router)
    app.include_router(ejemplos.router)
    app.include_router(historial.router)

    @app.get("/api/v1/health")
    def health() -> dict[str, str]:
        """CU-02: verificación de salud del servicio."""
        return {
            "status": "ok",
            "version": API_VERSION,
            "extractor_mode": config.extractor_mode,
        }

    return app


def __getattr__(name: str):  # pragma: no cover — verificado manualmente con uvicorn (DoD §5)
    """Construye `app` perezosamente para `uvicorn src.main:app`.

    Evita el efecto secundario de crear la base de datos real al importar el
    módulo (los tests llaman `create_app` con SQLite temporal); el primer
    acceso a `app` instancia la aplicación real y la cachea.
    """
    if name == "app":
        instance = create_app()
        globals()["app"] = instance
        return instance
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
