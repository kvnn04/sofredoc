"""Extractor mock: fixtures deterministas sin red (DESIGN-02 §5, RN-2-05).

`EXTRACTOR_MODE=mock` (default): responde sin créditos de IA. La variante
(`MOCK_VARIANT`) elige la fixture para archivos no reconocidos; además, si el
nombre del archivo identifica uno de los 3 ejemplos de la demo (el frontend
lo sube como `{id}.pdf`, matriz de verdad de MOD-03), se devuelve la fixture
de ese escenario. Así el modo mock reproduce APROBADO / RECHAZADO-R3 /
RECHAZADO-R4 igual que `EXTRACTOR_MODE=llm` (ADR-05-01).
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
    "monto-alto-sin-oc": "extraccion-monto-alto-sin-oc.json",  # > $500.000 sin OC => R4
    "remito": "extraccion-remito.json",  # tipo REMITO => admisión R0 (REMITO_NO_AUDITABLE)
}

# (marca en el nombre de archivo, variante de fixture): cubre tanto el id del
# catálogo (`ej-monto-alto-sin-oc.pdf`) como el nombre original del PDF de
# ejemplo (`factura-monto-alto-sin-oc.pdf`) re-subido a mano, y los archivos
# cuyo nombre contiene "remito" (E2E: remito → R0).
MARCAS_EJEMPLOS: tuple[tuple[str, str], ...] = (
    ("ej-factura-aprobada", "aprobada"),
    ("factura-aprobada-001", "aprobada"),
    ("ej-factura-desvio", "rechazado"),
    ("factura-desvio-monto", "rechazado"),
    ("ej-monto-alto-sin-oc", "monto-alto-sin-oc"),
    ("factura-monto-alto-sin-oc", "monto-alto-sin-oc"),
    ("remito", "remito"),
)


class MockExtractor:
    """Devuelve la extracción de una fixture: misma entrada → misma salida."""

    def __init__(self, directorio: Path, variante: str = "aprobada") -> None:
        if variante not in VARIANTES:
            raise ValueError(f"MOCK_VARIANT='{variante}' inválida; variantes: {sorted(VARIANTES)}")
        self._variante = variante
        self._fixtures: dict[str, tuple[dict, FacturaExtraida]] = {}
        for clave, archivo in VARIANTES.items():
            ruta = directorio / archivo
            if not ruta.is_file():
                raise ExtraccionFallidaError(f"Fixture mock inexistente: {ruta}")
            crudo = json.loads(ruta.read_text(encoding="utf-8"))
            # Garantiza que cada fixture valida 100% contra el esquema (RN-2-03).
            self._fixtures[clave] = (crudo, FacturaExtraida.model_validate(crudo))

    def extraer(self, texto_pdf: str, nombre_archivo: str) -> ExtraccionResultado:
        """Respuesta inmediata (< 10 ms) y determinista para la misma entrada.

        Si `nombre_archivo` identifica un ejemplo de la demo se usa su fixture
        (matriz de verdad); si no, la variante configurada (`MOCK_VARIANT`).
        """
        inicio = time.perf_counter()
        clave = self._variante
        marca = nombre_archivo.lower()
        for sello, variante_ejemplo in MARCAS_EJEMPLOS:
            if sello in marca:
                clave = variante_ejemplo
                break
        crudo, factura = self._fixtures[clave]
        resultado = ExtraccionResultado(factura=factura, json_crudo_ia=crudo)
        logger.debug(
            "MockExtractor (fixture %s) en %.2f ms | texto=%.0f chars | archivo=%s",
            clave,
            (time.perf_counter() - inicio) * 1000,
            len(texto_pdf),
            nombre_archivo,
        )
        return resultado
