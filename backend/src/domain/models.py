"""Modelos de dominio: factura extraída y resultados de auditoría (DESIGN-01 §2)."""

from datetime import date
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, Field


class ItemFactura(BaseModel):
    """Ítem de la factura tal como fue extraído (la IA no corrige datos).

    Las `description` viajan al JSON Schema strict del proveedor
    (ADR-02-10/11): definen la semántica AFIP/ARCA que el LLM no puede inferir
    de nombres genéricos.
    """

    descripcion: str = Field(
        min_length=1,
        description="Descripción literal del ítem tal como figura en el comprobante.",
    )
    cantidad: Decimal = Field(
        gt=0,
        description="Cantidad del ítem según el comprobante (número, sin 'Unid.' ni texto).",
    )
    precio_unitario: Decimal = Field(
        ge=0,
        description=(
            "Precio unitario según la letra del comprobante (ver "
            "letra_comprobante): en Factura A (IVA discriminado) es el precio "
            "SIN IVA; en Factura B o C es el precio final de la línea con IVA "
            "incluido."
        ),
    )
    subtotal: Decimal = Field(
        ge=0,
        description=(
            "Subtotal de la línea según la letra del comprobante (ver "
            "letra_comprobante): en Factura A (IVA discriminado) es el valor "
            "neto SIN IVA (columna 'Subtotal Neto', NUNCA 'Subtotal c/IVA'); en "
            "Factura B o C es el importe final de la línea con IVA incluido. Si "
            "el comprobante informa el recuado de Transparencia Fiscal (Ley "
            "27.743, 'IVA Contenido'), ese IVA ya está dentro de este subtotal: "
            "no restarlo ni sumarlo."
        ),
    )


class FacturaExtraida(BaseModel):
    """Comprobante estructurado producido por la extracción (MOD-02)."""

    tipo_comprobante: Literal["FACTURA", "REMITO"]
    letra_comprobante: str | None = Field(
        default=None,
        description=(
            "Letra del comprobante fiscal según el encabezado, como letra "
            "mayúscula sola ('A', 'B', 'C' o la que corresponda, p. ej. 'M'); "
            "null para REMITO o si no se indica letra. Extraerla primero: define "
            "si los ítems son netos (A) o con IVA incluido (B, C) y qué impuestos "
            "se adicionan."
        ),
    )
    numero_comprobante: str | None = None
    cuit_emisor: str  # se normaliza y valida con el VO CUIT en las reglas
    razon_social: str = Field(min_length=1)
    fecha_emision: date
    numero_orden_compra: str | None = None
    items: list[ItemFactura] = Field(min_length=1)
    impuestos: Decimal = Field(
        default=Decimal("0.00"),
        description=(
            "Impuestos que se ADICIONAN a los subtotales de los ítems para "
            "llegar al total (la ecuación es: suma de ítems + impuestos = "
            "total). Según la letra del comprobante (ver letra_comprobante): "
            "- Factura A (IVA discriminado): suma de TODOS los impuestos "
            "discriminados al pie (IVA 21% + IVA 10,5% + IVA 27% + impuestos "
            "internos + percepciones + 'Importe Otros Tributos'), no únicamente "
            "esa última fila; NUNCA es 0 si el pie informa un monto de IVA. "
            "- Factura B o C (IVA incluido en el precio): 0 si entre los "
            "subtotales y el total no se suma nada. NO cargar aquí el recuado "
            "informativo del Régimen de Transparencia Fiscal al Consumidor (Ley "
            "27.743) — 'IVA Contenido' / 'IVA Contenido (incluido en el precio "
            "final)' / 'Otros Impuestos Nacionales Indirectos' — porque ya está "
            "INCLUIDO en el total y en los subtotales de los ítems (no se "
            "adiciona). Solo sumar percepciones u otros tributos que figuren "
            "como línea adicional entre los subtotales y el total (p. ej. "
            "'Percepciones / Otros Tributos' mayor a 0)."
        ),
    )
    monto_total: Decimal = Field(
        gt=0,
        description=(
            "IMPORTE TOTAL del comprobante tal como figura al pie (neto + "
            "impuestos); no confundir con 'Importe Neto Gravado'."
        ),
    )


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


class RegistroAuditoria(BaseModel):
    """Auditoría completa tal como se persiste en el historial y se sirve (MOD-03).

    `ERROR_EXTRACCION` es un estado de tabla (trazabilidad, RN-3-03): no alcanza
    al semáforo de reglas, por eso `reglas_evaluadas` queda vacía en ese caso.
    """

    id: str  # `aud_` + 8 hex (convención global de specs/README.md)
    nombre_archivo: str
    estado: Literal["APROBADO", "RECHAZADO", "ERROR_EXTRACCION"]
    cuit_emisor: str | None = None  # NULL si la extracción falló
    monto_total: Decimal | None = None  # NULL si la extracción falló
    datos_extraidos: dict | None = None  # FacturaExtraida serializada (JSON) o None
    reglas_evaluadas: list[ReglaResultado] = Field(default_factory=list)
    json_crudo_ia: dict | None = None  # trazabilidad del output crudo del LLM
    tiempo_ejecucion_ms: int = Field(ge=0)
    latencia_extraccion_ms: int = Field(ge=0)  # etapa IA
    latencia_reglas_ms: int = Field(ge=0)  # etapa motor de reglas
    creado_en: str  # ISO 8601 UTC (YYYY-MM-DDTHH:MM:SSZ)
