"""R3 — Consistencia matemática: Σ(cantidad × precio) + impuestos == total ± $1.00 (RN-03)."""

from decimal import Decimal

from src.domain.models import FacturaExtraida, ReglaResultado
from src.domain.rules.base import ContextoAuditoria, formato_ars

CODIGO_ERROR = "DISCREPANCIA_CONTABLE"
TOLERANCIA = Decimal("1.00")


def calculo_total(factura: FacturaExtraida) -> Decimal:
    """Σ(cantidad × precio unitario) + impuestos — la ecuación de R3 (RN-03).

    Fuente única (ADR-02-12): el extractor la reutiliza como gate de
    consistencia pre-reintento, así el chequeo y la regla nunca divergen.
    """
    return (
        sum((item.cantidad * item.precio_unitario for item in factura.items), Decimal("0.00"))
        + factura.impuestos
    )


class R3ConsistenciaMatematica:
    """Recalcula el total con Decimal exacto; tolerancia estricta de ± $1.00 ARS."""

    codigo = "R3"
    nombre = "Consistencia matemática"

    def evaluar(self, factura: FacturaExtraida, ctx: ContextoAuditoria) -> ReglaResultado:
        calculado = calculo_total(factura)
        if abs(calculado - factura.monto_total) <= TOLERANCIA:
            return ReglaResultado(
                codigo=self.codigo,
                nombre=self.nombre,
                aprobado=True,
                mensaje="Suma de ítems + impuestos coincide con el total.",
            )
        return ReglaResultado(
            codigo=self.codigo,
            nombre=self.nombre,
            aprobado=False,
            mensaje=(
                "La suma de ítems + impuestos "
                f"({formato_ars(calculado)}) no coincide con el total declarado "
                f"({formato_ars(factura.monto_total)})."
            ),
            codigo_error=CODIGO_ERROR,
            detalles={
                "calculado": f"{calculado.quantize(Decimal('0.01')):f}",
                "declarado": f"{factura.monto_total.quantize(Decimal('0.01')):f}",
            },
        )
