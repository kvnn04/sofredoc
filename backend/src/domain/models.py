"""Modelos de dominio: factura extraída y resultados de auditoría (DESIGN-01 §2)."""

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class ItemFactura(BaseModel):
    """Ítem de la factura tal como fue extraído (la IA no corrige datos)."""

    descripcion: str = Field(min_length=1)
    cantidad: Decimal = Field(gt=0)
    precio_unitario: Decimal = Field(ge=0)
    subtotal: Decimal = Field(ge=0)


class FacturaExtraida(BaseModel):
    """Comprobante estructurado producido por la extracción (MOD-02)."""

    tipo_comprobante: Literal["FACTURA", "REMITO"]
    numero_comprobante: str | None = None
    cuit_emisor: str  # se normaliza y valida con el VO CUIT en las reglas
    razon_social: str = Field(min_length=1)
    fecha_emision: date
    numero_orden_compra: str | None = None
    items: list[ItemFactura] = Field(min_length=1)
    impuestos: Decimal = Decimal("0.00")
    monto_total: Decimal = Field(gt=0)


class ExtraccionResultado(BaseModel):
    """Salida del extractor (MOD-02): factura validada + JSON crudo del LLM."""

    factura: FacturaExtraida
    json_crudo_ia: dict | None = None  # trazabilidad del output crudo (RN-2-04)


class ReglaResultado(BaseModel):
    """Resultado individual de una regla (fila del semáforo)."""

    codigo: Literal["R0", "R1", "R2", "R3", "R4", "R5"]
    nombre: str
    aprobado: bool
    mensaje: str  # legible para el operador
    codigo_error: str | None = None  # ej. DISCREPANCIA_CONTABLE
    detalles: dict[str, str] | None = None  # ej. {"calculado": "270000.00", ...}


class ResultadoAuditoria(BaseModel):
    """Estado global del comprobante + detalle de cada regla evaluada."""

    estado: Literal["APROBADO", "RECHAZADO"]
    reglas: list[ReglaResultado]

    @classmethod
    def desde_reglas(cls, reglas: list[ReglaResultado]) -> "ResultadoAuditoria":
        """APROBADO solo si todas las reglas pasan; cualquier fallo => RECHAZADO."""
        estado = "APROBADO" if all(r.aprobado for r in reglas) else "RECHAZADO"
        return cls(estado=estado, reglas=reglas)
