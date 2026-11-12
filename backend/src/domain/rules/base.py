"""Base del motor: Protocol Regla, ContextoAuditoria y formato es-AR de montos."""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Protocol

from src.domain.models import FacturaExtraida, ReglaResultado
from src.domain.ports.padron_port import Proveedor


@dataclass(frozen=True)
class ContextoAuditoria:
    """Dependencias inyectables para evaluar reglas: 'hoy' del reloj y proveedor del padrón."""

    hoy: date
    proveedor: Proveedor | None = None


class Regla(Protocol):
    """Contrato de una regla de negocio evaluable (R0–R5)."""

    codigo: str
    nombre: str

    def evaluar(self, factura: FacturaExtraida, ctx: ContextoAuditoria) -> ReglaResultado: ...


def formato_ars(monto: Decimal) -> str:
    """Formatea un monto Decimal como texto es-AR con 2 decimales: $270.000,00 / -$5.000,00."""
    cuantizado = monto.quantize(Decimal("0.01"))
    texto = f"{cuantizado:f}"
    negativo = texto.startswith("-")
    entero, _, decimales = texto.removeprefix("-").partition(".")
    grupos: list[str] = []
    while len(entero) > 3:
        grupos.insert(0, entero[-3:])
        entero = entero[:-3]
    if entero:
        grupos.insert(0, entero)
    cuerpo = f"{'.'.join(grupos)},{decimales}"
    return f"-${cuerpo}" if negativo else f"${cuerpo}"
