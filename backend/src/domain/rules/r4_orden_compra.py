"""R4 — Tope sin Orden de Compra: monto > $500.000 exige OC (RN-04)."""

from decimal import Decimal

from src.domain.models import FacturaExtraida, ReglaResultado
from src.domain.rules.base import ContextoAuditoria, formato_ars

CODIGO_ERROR = "FALTA_ORDEN_COMPRA"
TOPE = Decimal("500000.00")


class R4TopeSinOrdenCompra:
    """Tope estricto: con monto == $500.000 no se exige OC; con OC siempre aprueba."""

    codigo = "R4"
    nombre = "Tope sin Orden de Compra"

    def evaluar(self, factura: FacturaExtraida, ctx: ContextoAuditoria) -> ReglaResultado:
        numero = factura.numero_orden_compra
        tiene_oc = numero is not None and numero.strip() != ""
        if factura.monto_total <= TOPE:
            mensaje = "OC presente." if tiene_oc else "Monto bajo el tope, OC no requerida."
            return ReglaResultado(
                codigo=self.codigo,
                nombre=self.nombre,
                aprobado=True,
                mensaje=mensaje,
            )
        if tiene_oc:
            return ReglaResultado(
                codigo=self.codigo,
                nombre=self.nombre,
                aprobado=True,
                mensaje="OC presente.",
            )
        return ReglaResultado(
            codigo=self.codigo,
            nombre=self.nombre,
            aprobado=False,
            mensaje=(
                f"Comprobante de {formato_ars(factura.monto_total)} supera el tope "
                f"de {formato_ars(TOPE)} sin Orden de Compra."
            ),
            codigo_error=CODIGO_ERROR,
        )
