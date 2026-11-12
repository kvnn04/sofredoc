"""R2 — Proveedor habilitado: CUIT registrado y activo en el padrón (RN-02)."""

from src.domain.models import FacturaExtraida, ReglaResultado
from src.domain.rules.base import ContextoAuditoria

CODIGO_ERROR = "PROVEEDOR_NO_REGISTRADO"


class R2ProveedorHabilitado:
    """Aplica tanto a CUIT ausente del padrón como a proveedor inactivo."""

    codigo = "R2"
    nombre = "Proveedor habilitado"

    def evaluar(self, factura: FacturaExtraida, ctx: ContextoAuditoria) -> ReglaResultado:
        if ctx.proveedor is not None and ctx.proveedor.activo:
            return ReglaResultado(
                codigo=self.codigo,
                nombre=self.nombre,
                aprobado=True,
                mensaje="Proveedor activo en el padrón.",
            )
        return ReglaResultado(
            codigo=self.codigo,
            nombre=self.nombre,
            aprobado=False,
            mensaje="El CUIT no se encuentra registrado o activo en el padrón de proveedores.",
            codigo_error=CODIGO_ERROR,
        )
