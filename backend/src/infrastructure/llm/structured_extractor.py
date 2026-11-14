"""Adapter DocumentExtractorPort con Structured Outputs (DESIGN-02 §5).

Pipeline: prompt + JSON Schema → dict crudo del proveedor → validación estricta
de Pydantic (`FacturaExtraida`). Máximo 1 reintento (RN-2-03), ahora sobre
ValidationError O sobre inconsistencia aritmética (ecuación de R3 como gate,
ADR-02-12); el JSON crudo se conserva para trazabilidad (RN-2-04).
"""

import logging
import time

from pydantic import ValidationError

from src.domain.errors import ExtraccionFallidaError
from src.domain.models import ExtraccionResultado, FacturaExtraida
from src.domain.rules.r3_matematica import TOLERANCIA, calculo_total
from src.infrastructure.llm.client import completar_con_esquema
from src.infrastructure.llm.prompt import SYSTEM_PROMPT, build_user_prompt

logger = logging.getLogger(__name__)

INTENTOS_MAXIMOS = 2  # intento inicial + 1 reintento (RN-2-03)

# Campos DERIVADOS que el LLM no recibe en su esquema (ADR-02-12): se calculan
# en Python sobre la entidad ya validada. Pedirle `impuestos` al modelo lo
# obligaba a sumar las líneas del pie de memoria (bug real: devolvió 94.600
# por 145.800 en una Factura A con alícuotas mixtas y percepción).
_CAMPOS_CALCULADOS = ("impuestos",)


def esquema_para_llm() -> dict:
    """JSON Schema de `FacturaExtraida` sin los campos calculados en Python.

    `preparar_esquema_estricto` regenera `required` desde `properties`, así
    que basta con retirarlos de las propiedades del esquema crudo.
    """
    esquema = FacturaExtraida.model_json_schema()
    for campo in _CAMPOS_CALCULADOS:
        esquema["properties"].pop(campo, None)
    return esquema


def _consistente(factura: FacturaExtraida) -> bool:
    """La ecuación de R3 (RN-03) como gate pre-reintento (ADR-02-12).

    Σ(cantidad × precio) + impuestos == total ± $1.00 con la MISMA fuente que
    la regla (`calculo_total` + `TOLERANCIA`), para que el chequeo y R3 nunca
    diverjan. Solo FACTURA: en REMITO decide R0 antes de cualquier matemática.
    Si ningún intento cuadra, se devuelve el último validado y R3 decide
    (RECHAZADO = 200 OK): nunca se "corrigen" los datos extraídos.
    """
    if factura.tipo_comprobante != "FACTURA":
        return True
    return abs(calculo_total(factura) - factura.monto_total) <= TOLERANCIA


class LLMStructuredExtractor:
    """Texto del PDF → `FacturaExtraida` validada por Pydantic (la IA solo extrae)."""

    def __init__(self, proveedor: str, modelo: str) -> None:
        self._proveedor = proveedor
        self._modelo = modelo

    def extraer(self, texto_pdf: str, nombre_archivo: str) -> ExtraccionResultado:
        esquema = esquema_para_llm()
        inicio = time.perf_counter()
        ultimo_error: ValidationError | None = None
        ultima_valida: tuple[FacturaExtraida, dict] | None = None

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

            if _consistente(factura):
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

            ultima_valida = (factura, crudo)
            logger.warning(
                "Intento %d aritméticamente inconsistente (Σ items + impuestos != total, "
                "tolerancia ± $%.2f): reintento con prompt reforzado",
                intento,
                TOLERANCIA,
            )

        if ultima_valida is not None:
            # Ningún intento cuadró la ecuación: sale el último validado y el
            # semáforo mostrará R3 en rojo (resultado de negocio, 200 OK).
            factura, crudo = ultima_valida
            logger.warning(
                "Extracción sin cuadrar tras %d intentos (archivo=%s); R3 decidirá.",
                INTENTOS_MAXIMOS,
                nombre_archivo,
            )
            return ExtraccionResultado(factura=factura, json_crudo_ia=crudo)

        detalle = str(ultimo_error)[:500] if ultimo_error else "sin detalle"
        raise ExtraccionFallidaError(
            f"La respuesta del LLM no validó contra el esquema tras "
            f"{INTENTOS_MAXIMOS} intentos: {detalle}"
        )
