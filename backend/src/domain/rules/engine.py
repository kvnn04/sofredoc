"""Motor de reglas: admisión R0 y evaluación completa (sin cortocircuito) de R1–R5."""

from collections.abc import Sequence

from src.domain.models import FacturaExtraida, ReglaResultado, ResultadoAuditoria
from src.domain.rules.base import ContextoAuditoria, Regla
from src.domain.rules.r1_cuit import R1IntegridadCuit
from src.domain.rules.r2_proveedor import R2ProveedorHabilitado
from src.domain.rules.r3_matematica import R3ConsistenciaMatematica
from src.domain.rules.r4_orden_compra import R4TopeSinOrdenCompra
from src.domain.rules.r5_vigencia import R5VigenciaComprobante

REGLAS_BASE: tuple[Regla, ...] = (
    R1IntegridadCuit(),
    R2ProveedorHabilitado(),
    R3ConsistenciaMatematica(),
    R4TopeSinOrdenCompra(),
    R5VigenciaComprobante(),
)


class R0AdmisionComprobante:
    """RN-08: solo FACTURA es auditable; un REMITO corta el flujo antes de R1–R5."""

    codigo = "R0"
    nombre = "Admisión de comprobante"

    def evaluar(self, factura: FacturaExtraida, ctx: ContextoAuditoria) -> ReglaResultado:
        if factura.tipo_comprobante == "FACTURA":
            return ReglaResultado(
                codigo=self.codigo,
                nombre=self.nombre,
                aprobado=True,
                mensaje="Comprobante FACTURA: auditable.",
            )
        return ReglaResultado(
            codigo=self.codigo,
            nombre=self.nombre,
            aprobado=False,
            mensaje="Comprobante tipo REMITO: fuera de alcance del MVP (solo se auditan facturas).",
            codigo_error="REMITO_NO_AUDITABLE",
        )


class MotorReglas:
    """Evaluador agregado: R0 decide la admisión; luego corren todas las reglas inyectadas.

    El resultado global se arma con `ResultadoAuditoria.desde_reglas`; las reglas
    son inyectables (default R1–R5) para facilitar tests y futuros casos de uso.
    """

    def __init__(self, reglas: Sequence[Regla] | None = None) -> None:
        self._reglas: tuple[Regla, ...] = tuple(reglas) if reglas is not None else REGLAS_BASE
        self._admision = R0AdmisionComprobante()

    def evaluar(self, factura: FacturaExtraida, ctx: ContextoAuditoria) -> ResultadoAuditoria:
        admision = self._admision.evaluar(factura, ctx)
        if not admision.aprobado:
            return ResultadoAuditoria.desde_reglas([admision])
        resultados = [regla.evaluar(factura, ctx) for regla in self._reglas]
        return ResultadoAuditoria.desde_reglas(resultados)
