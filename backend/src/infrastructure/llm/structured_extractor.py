"""Adapter DocumentExtractorPort con Structured Outputs (DESIGN-02 §5).

Pipeline: prompt + JSON Schema → dict crudo del proveedor → validación estricta
de Pydantic (`FacturaExtraida`). Máximo 1 reintento sobre ValidationError
(RN-2-03); el JSON crudo se conserva para trazabilidad (RN-2-04).
"""

import logging
import time

from pydantic import ValidationError

from src.domain.errors import ExtraccionFallidaError
from src.domain.models import ExtraccionResultado, FacturaExtraida
from src.infrastructure.llm.client import completar_con_esquema
from src.infrastructure.llm.prompt import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)

INTENTOS_MAXIMOS = 2  # intento inicial + 1 reintento (RN-2-03)


class LLMStructuredExtractor:
    """Texto del PDF → `FacturaExtraida` validada por Pydantic (la IA solo extrae)."""

    def __init__(self, proveedor: str, modelo: str) -> None:
        self._proveedor = proveedor
        self._modelo = modelo

    def extraer(self, texto_pdf: str, nombre_archivo: str) -> ExtraccionResultado:
        esquema = FacturaExtraida.model_json_schema()
        inicio = time.perf_counter()
        ultimo_error: ValidationError | None = None

        for intento in range(1, INTENTOS_MAXIMOS + 1):
            crudo = completar_con_esquema(
                system=SYSTEM_PROMPT,
                user=build_user_prompt(texto_pdf, nombre_archivo, intento=intento),
                esquema_json=esquema,
                temperatura=0,
            )
            try:
                factura = FacturaExtraida.model_validate(crudo)
            except ValidationError as exc:
                ultimo_error = exc
                logger.warning("Intento %d no validó contra el esquema: %s", intento, exc)
                continue

            latencia_ms = (time.perf_counter() - inicio) * 1000
            logger.info(
                "Extracción OK (%s/%s) en %.0f ms, intento %d, archivo=%s",
                self._proveedor,
                self._modelo,
                latencia_ms,
                intento,
                nombre_archivo,
            )
            return ExtraccionResultado(factura=factura, json_crudo_ia=crudo)

        detalle = str(ultimo_error)[:500] if ultimo_error else "sin detalle"
        raise ExtraccionFallidaError(
            f"La respuesta del LLM no validó contra el esquema tras "
            f"{INTENTOS_MAXIMOS} intentos: {detalle}"
        )
