"""Extractor mock: fixture determinista sin red (DESIGN-02 §5, RN-2-05).

`EXTRACTOR_MODE=mock` (default): devuelve siempre la misma `FacturaExtraida`
de fixture, sin créditos de IA. La variante (`MOCK_VARIANT`) permite probar el
camino RECHAZADO en demos y pruebas de carga.
"""

import json
import logging
import time
from pathlib import Path

from src.domain.errors import ExtraccionFallidaError
from src.domain.models import ExtraccionResultado, FacturaExtraida

logger = logging.getLogger(__name__)

VARIANTES: dict[str, str] = {
    "aprobada": "extraccion-esperada.json",
    "rechazado": "extraccion-rechazado.json",  # desvío de monto > $1.00 => R3
}


class MockExtractor:
    """Devuelve la extracción del fixture: misma entrada → misma salida."""

    def __init__(self, directorio: Path, variante: str = "aprobada") -> None:
        if variante not in VARIANTES:
            raise ValueError(
                f"MOCK_VARIANT='{variante}' inválida; variantes: {sorted(VARIANTES)}"
            )
        self._variante = variante
        ruta = directorio / VARIANTES[variante]
        if not ruta.is_file():
            raise ExtraccionFallidaError(f"Fixture mock inexistente: {ruta}")
        self._crudo = json.loads(ruta.read_text(encoding="utf-8"))
        # Garantiza que el fixture valida 100% contra el esquema (RN-2-03).
        self._factura = FacturaExtraida.model_validate(self._crudo)

    def extraer(self, texto_pdf: str, nombre_archivo: str) -> ExtraccionResultado:
        """Respuesta inmediata (~5 ms) e independiente del contenido recibido."""
        inicio = time.perf_counter()
        resultado = ExtraccionResultado(factura=self._factura, json_crudo_ia=self._crudo)
        logger.debug(
            "MockExtractor (variante %s) en %.2f ms | texto=%.0f chars | archivo=%s",
            self._variante,
            (time.perf_counter() - inicio) * 1000,
            len(texto_pdf),
            nombre_archivo,
        )
        return resultado
