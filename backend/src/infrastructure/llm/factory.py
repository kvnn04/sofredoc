"""Fábrica del extractor según `EXTRACTOR_MODE` (DESIGN-02 §1, T-09)."""

from pathlib import Path

from src.config import Settings, get_settings
from src.domain.ports.document_extractor_port import DocumentExtractorPort
from src.infrastructure.llm.mock_extractor import MockExtractor
from src.infrastructure.llm.structured_extractor import LLMStructuredExtractor

# backend/src/infrastructure/llm/ → backend/data/fixtures/
_RUTA_FIXTURES = Path(__file__).resolve().parents[3] / "data" / "fixtures"


def crear_extractor(config: Settings | None = None) -> DocumentExtractorPort:
    """Devuelve el extractor configurado: mock (default) o LLM con API key."""
    config = config or get_settings()

    if config.extractor_mode == "mock":
        return MockExtractor(_RUTA_FIXTURES, variante=config.mock_variant)

    if not config.llm_api_key:
        raise RuntimeError("EXTRACTOR_MODE=llm requiere LLM_API_KEY configurada (backend/.env).")
    return LLMStructuredExtractor(proveedor=config.llm_provider, modelo=config.llm_model)
