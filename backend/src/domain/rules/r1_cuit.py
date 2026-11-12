"""R1 — Integridad de CUIT: 11 dígitos y dígito verificador Módulo 11 (RN-01)."""

from src.domain.models import FacturaExtraida, ReglaResultado
from src.domain.rules.base import ContextoAuditoria
from src.domain.value_objects.cuit import CUIT

CODIGO_ERROR = "ERROR_CUIT_INVALIDO"


class R1IntegridadCuit:
    """Rechaza CUITs con formato inválido o dígito verificador incorrecto."""

    codigo = "R1"
    nombre = "Integridad de CUIT"

    def evaluar(self, factura: FacturaExtraida, ctx: ContextoAuditoria) -> ReglaResultado:
        if CUIT(factura.cuit_emisor).es_valido():
            return ReglaResultado(
                codigo=self.codigo,
                nombre=self.nombre,
                aprobado=True,
                mensaje="CUIT válido (dígito verificador correcto).",
            )
        return ReglaResultado(
            codigo=self.codigo,
            nombre=self.nombre,
            aprobado=False,
            mensaje="CUIT con dígito verificador incorrecto o formato inválido.",
            codigo_error=CODIGO_ERROR,
        )
