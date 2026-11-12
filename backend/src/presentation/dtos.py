"""DTOs de la capa de presentación (contratos HTTP de DESIGN-03 §2/§3).

Traducen `RegistroAuditoria` (dominio) a los cuerpos de la API: los montos
`Decimal` se exponen como número con 2 decimales (convención global).
"""

from decimal import Decimal
from typing import Literal

from pydantic import BaseModel

from src.domain.models import RegistroAuditoria


def _numero(monto: Decimal | None) -> float | None:
    """Decimal → número JSON con 2 decimales; None se conserva (extracción fallida)."""
    return None if monto is None else float(monto.quantize(Decimal("0.01")))


class ReglaResultadoDTO(BaseModel):
    """Fila del semáforo de reglas tal como se expone en la API."""

    codigo: str
    nombre: str
    aprobado: bool
    mensaje: str
    codigo_error: str | None = None
    detalles: dict[str, str] | None = None


class RegistroAuditoriaDTO(BaseModel):
    """Respuesta de `POST /api/v1/auditar` y de `GET /api/v1/historial/{id}`."""

    id: str
    estado: Literal["APROBADO", "RECHAZADO", "ERROR_EXTRACCION"]
    nombre_archivo: str
    cuit_emisor: str | None = None
    monto_total: float | None = None
    datos_extraidos: dict | None = None
    reglas_evaluadas: list[ReglaResultadoDTO]
    json_crudo_ia: dict | None = None
    tiempo_ejecucion_ms: int
    latencia_extraccion_ms: int
    latencia_reglas_ms: int
    creado_en: str

    @classmethod
    def desde_registro(cls, registro: RegistroAuditoria) -> "RegistroAuditoriaDTO":
        """Construye el DTO desde el modelo de dominio (o de la fila SQLite)."""
        return cls(
            id=registro.id,
            estado=registro.estado,
            nombre_archivo=registro.nombre_archivo,
            cuit_emisor=registro.cuit_emisor,
            monto_total=_numero(registro.monto_total),
            datos_extraidos=registro.datos_extraidos,
            reglas_evaluadas=[
                ReglaResultadoDTO(**regla.model_dump()) for regla in registro.reglas_evaluadas
            ],
            json_crudo_ia=registro.json_crudo_ia,
            tiempo_ejecucion_ms=registro.tiempo_ejecucion_ms,
            latencia_extraccion_ms=registro.latencia_extraccion_ms,
            latencia_reglas_ms=registro.latencia_reglas_ms,
            creado_en=registro.creado_en,
        )


class ResumenAuditoriaDTO(BaseModel):
    """Ítem del listado `GET /api/v1/historial`: igual al detalle sin `json_crudo_ia` (CU-04)."""

    id: str
    estado: Literal["APROBADO", "RECHAZADO", "ERROR_EXTRACCION"]
    nombre_archivo: str
    cuit_emisor: str | None = None
    monto_total: float | None = None
    datos_extraidos: dict | None = None
    reglas_evaluadas: list[ReglaResultadoDTO]
    tiempo_ejecucion_ms: int
    latencia_extraccion_ms: int
    latencia_reglas_ms: int
    creado_en: str

    @classmethod
    def desde_registro(cls, registro: RegistroAuditoria) -> "ResumenAuditoriaDTO":
        """Construye el ítem de listado descartando el JSON crudo del LLM."""
        completo = RegistroAuditoriaDTO.desde_registro(registro)
        return cls(**completo.model_dump(exclude={"json_crudo_ia"}))
