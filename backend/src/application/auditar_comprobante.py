"""Caso de uso: auditar un comprobante end-to-end (DESIGN-03 §1, CU-01/02).

Orquesta PDF → extracción (IA/mock) → motor de reglas → persistencia. La API
no contiene lógica de negocio (RN-3-06): todo se delega acá y al dominio.
"""

import secrets
import time
from datetime import UTC, date, datetime
from decimal import Decimal

from src.domain.errors import ExtraccionFallidaError
from src.domain.models import FacturaExtraida, RegistroAuditoria, ResultadoAuditoria
from src.domain.ports.auditoria_repository_port import AuditoriaRepositoryPort
from src.domain.ports.clock_port import ClockPort
from src.domain.ports.document_extractor_port import DocumentExtractorPort
from src.domain.ports.padron_port import PadronProveedoresPort
from src.domain.ports.pdf_text_port import PdfTextPort
from src.domain.rules.base import ContextoAuditoria
from src.domain.rules.engine import MotorReglas


def serializar_datos(factura: FacturaExtraida) -> dict:
    """Factura → dict JSON: montos numéricos con 2 decimales y fecha ISO.

    pydantic serializa `Decimal` como string en modo JSON; la convención global
    exige montos numéricos con 2 decimales, así que se convierten explícitamente.
    """

    def convertir(valor):
        if isinstance(valor, Decimal):
            return float(valor.quantize(Decimal("0.01")))
        if isinstance(valor, date):
            return valor.isoformat()
        if isinstance(valor, dict):
            return {clave: convertir(item) for clave, item in valor.items()}
        if isinstance(valor, list):
            return [convertir(item) for item in valor]
        return valor

    return convertir(factura.model_dump())


class AuditarComprobanteUseCase:
    """Ejecuta el flujo completo con puertos inyectados y latencias por etapa."""

    def __init__(
        self,
        *,
        pdf_port: PdfTextPort,
        extractor: DocumentExtractorPort,
        padron: PadronProveedoresPort,
        clock: ClockPort,
        repo: AuditoriaRepositoryPort,
        motor: MotorReglas | None = None,
    ) -> None:
        self._pdf = pdf_port
        self._extractor = extractor
        self._padron = padron
        self._clock = clock
        self._repo = repo
        self._motor = motor or MotorReglas()

    def ejecutar(self, contenido_pdf: bytes, nombre_archivo: str) -> RegistroAuditoria:
        """Audita el PDF y devuelve el registro persistido (RN-3-03).

        - Errores de PDF (parseo, >10 páginas, sin texto) se propagan sin
          persistir: la presentación los mapea a `422`.
        - Un fallo de extracción se persiste como `ERROR_EXTRACCION` (fila de
          trazabilidad con `reglas_evaluadas=[]`) y luego se propaga (`502`).
        """
        inicio = time.perf_counter()

        texto_pdf = self._pdf.extraer_texto(contenido_pdf)

        inicio_extraccion = time.perf_counter()
        try:
            extraccion = self._extractor.extraer(texto_pdf, nombre_archivo)
        except ExtraccionFallidaError:
            self._repo.guardar(
                RegistroAuditoria(
                    id=_nuevo_id(),
                    nombre_archivo=nombre_archivo,
                    estado="ERROR_EXTRACCION",
                    latencia_extraccion_ms=_ms(inicio_extraccion, time.perf_counter()),
                    latencia_reglas_ms=0,
                    tiempo_ejecucion_ms=_ms(inicio, time.perf_counter()),
                    creado_en=_ahora_utc(),
                )
            )
            raise
        latencia_extraccion = _ms(inicio_extraccion, time.perf_counter())

        factura = extraccion.factura
        inicio_reglas = time.perf_counter()
        contexto = ContextoAuditoria(
            hoy=self._clock.hoy(),
            proveedor=self._padron.buscar(factura.cuit_emisor),
        )
        resultado: ResultadoAuditoria = self._motor.evaluar(factura, contexto)
        latencia_reglas = _ms(inicio_reglas, time.perf_counter())

        registro = RegistroAuditoria(
            id=_nuevo_id(),
            nombre_archivo=nombre_archivo,
            estado=resultado.estado,
            cuit_emisor=factura.cuit_emisor,
            monto_total=factura.monto_total,
            datos_extraidos=serializar_datos(factura),
            reglas_evaluadas=resultado.reglas,
            json_crudo_ia=extraccion.json_crudo_ia,
            latencia_extraccion_ms=latencia_extraccion,
            latencia_reglas_ms=latencia_reglas,
            tiempo_ejecucion_ms=_ms(inicio, time.perf_counter()),
            creado_en=_ahora_utc(),
        )
        self._repo.guardar(registro)
        return registro


def _nuevo_id() -> str:
    """Id de auditoría: `aud_` + 8 hex (convención global de specs/README.md)."""
    return f"aud_{secrets.token_hex(4)}"


def _ahora_utc() -> str:
    """Timestamp ISO 8601 UTC con sufijo Z (convención global)."""
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ms(inicio: float, fin: float) -> int:
    """Duración entre dos marcas de `perf_counter`, en ms enteros (≥ 0)."""
    return max(0, round((fin - inicio) * 1000))
