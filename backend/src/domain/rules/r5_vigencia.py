"""R5 — Vigencia del comprobante: 0–60 días de antigüedad, sin fechas futuras (RN-05)."""

from src.domain.models import FacturaExtraida, ReglaResultado
from src.domain.rules.base import ContextoAuditoria

CODIGO_ERROR = "COMPROBANTE_VENCIDO"
DIAS_VIGENCIA = 60


class R5VigenciaComprobante:
    """Emitida hoy = válida; a exactamente 60 días = válida; a 61 días o futura = rechaza."""

    codigo = "R5"
    nombre = "Vigencia del comprobante"

    def evaluar(self, factura: FacturaExtraida, ctx: ContextoAuditoria) -> ReglaResultado:
        dias = (ctx.hoy - factura.fecha_emision).days
        if dias < 0:
            return ReglaResultado(
                codigo=self.codigo,
                nombre=self.nombre,
                aprobado=False,
                mensaje="Fecha de emisión futura.",
                codigo_error=CODIGO_ERROR,
            )
        if dias > DIAS_VIGENCIA:
            return ReglaResultado(
                codigo=self.codigo,
                nombre=self.nombre,
                aprobado=False,
                mensaje=f"Comprobante vencido (emitido hace {dias} días; tope {DIAS_VIGENCIA}).",
                codigo_error=CODIGO_ERROR,
            )
        return ReglaResultado(
            codigo=self.codigo,
            nombre=self.nombre,
            aprobado=True,
            mensaje=f"Fecha de emisión dentro de la vigencia ({DIAS_VIGENCIA} días).",
        )
