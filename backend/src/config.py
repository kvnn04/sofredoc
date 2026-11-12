"""Configuración central del backend (pydantic-settings).

Toda configuración externa se lee de variables de entorno (o de `.env`);
nunca se hardcodea (RN-00-05). Ver `backend/.env.example`.
"""

from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

_BASE_DIR = Path(__file__).resolve().parent.parent  # backend/
_REPO_DIR = _BASE_DIR.parent  # raíz del monorepo


class Settings(BaseSettings):
    """Variables de entorno del backend (tabla §2 de DESIGN-00)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "dev"
    api_port: int = 8000
    cors_origins: str = "http://localhost:5173"
    db_path: str = "backend/data/sofredoc.db"
    extractor_mode: Literal["mock", "llm"] = "mock"
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o-mini"
    llm_api_key: str | None = None
    mock_variant: str = "aprobada"  # fixture del MockExtractor para archivos no reconocidos
    padron_path: str = "backend/data/proveedores.json"
    max_pdf_mb: int = 5
    tz: str = "America/Argentina/Buenos_Aires"

    @property
    def cors_origins_list(self) -> list[str]:
        """Orígenes CORS como lista (admite separados por coma)."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def resolve_path(self, value: str) -> Path:
        """Resuelve una ruta relativa contra la raíz del monorepo."""
        path = Path(value)
        return path if path.is_absolute() else _REPO_DIR / path


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración singleton de la app."""
    return Settings()
