"""Pruebas del MotorReglas: admisión R0, estado global, fallos múltiples e inyección (T-16)."""

import json
import time
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

from src.domain.models import FacturaExtraida, ItemFactura
from src.domain.ports.clock_port import ClockPort
from src.domain.ports.padron_port import PadronProveedoresPort, Proveedor
from src.domain.rules.base import ContextoAuditoria
from src.domain.rules.engine import MotorReglas
from src.domain.rules.r1_cuit import R1IntegridadCuit
from src.domain.rules.r3_matematica import R3ConsistenciaMatematica

HOY = date(2026, 11, 12)
ACTIVO = Proveedor(cuit="30123456781", razon_social="Distribuidora Andina S.A.", activo=True)


def contexto(proveedor: Proveedor | None = ACTIVO) -> ContextoAuditoria:
    return ContextoAuditoria(hoy=HOY, proveedor=proveedor)


class TestEstadoGlobal:
    def test_factura_valida_aprueba(self, factura) -> None:
        """CU-01: las 5 reglas pasan y el estado global es APROBADO."""
        resultado = MotorReglas().evaluar(factura(), contexto())
        assert resultado.estado == "APROBADO"
        assert all(r.aprobado for r in resultado.reglas)
        assert [r.codigo for r in resultado.reglas] == ["R1", "R2", "R3", "R4", "R5"]

    def test_factura_invalida_rechaza(self, factura) -> None:
        resultado = MotorReglas().evaluar(
            factura(cuit_emisor="30-12345678-9"), contexto(proveedor=None)
        )
        assert resultado.estado == "RECHAZADO"
        fallidas = [(r.codigo, r.codigo_error) for r in resultado.reglas if not r.aprobado]
        assert fallidas == [("R1", "ERROR_CUIT_INVALIDO"), ("R2", "PROVEEDOR_NO_REGISTRADO")]


class TestFallosMultiples:
    def test_r3_y_r5_fallan_simultaneamente(self, factura) -> None:
        """CU-06 / fila 22: sin cortocircuito; se reportan 5 reglas y ambos fallos."""
        f = factura(
            monto_total=Decimal("285000.00"),  # R3 falla (suma 25000)
            fecha_emision=HOY - timedelta(days=75),  # R5 falla
            numero_orden_compra=None,  # R4 pasa (bajo tope)
        )
        resultado = MotorReglas().evaluar(f, contexto())
        assert resultado.estado == "RECHAZADO"
        assert len(resultado.reglas) == 5
        assert [r.codigo for r in resultado.reglas if not r.aprobado] == ["R3", "R5"]
        codigos = {r.codigo_error for r in resultado.reglas if r.codigo_error}
        assert codigos == {"DISCREPANCIA_CONTABLE", "COMPROBANTE_VENCIDO"}


class TestAdmisionR0:
    def test_remito_rechazado_solo_con_fila_r0(self, factura) -> None:
        """CU-07 / fila 23: R1–R5 no se evalúan para un REMITO."""
        resultado = MotorReglas().evaluar(factura(tipo_comprobante="REMITO"), contexto())
        assert resultado.estado == "RECHAZADO"
        assert [r.codigo for r in resultado.reglas] == ["R0"]
        assert resultado.reglas[0].codigo_error == "REMITO_NO_AUDITABLE"
        assert "REMITO" in resultado.reglas[0].mensaje

    def test_factura_no_incluye_fila_r0(self, factura) -> None:
        """Fila 24: para FACTURA corre la evaluación completa R1–R5."""
        resultado = MotorReglas().evaluar(factura(), contexto())
        assert "R0" not in [r.codigo for r in resultado.reglas]


class TestReglasInyectables:
    def test_subconjunto_aprobado(self, factura) -> None:
        motor = MotorReglas(reglas=[R1IntegridadCuit()])
        resultado = motor.evaluar(factura(), contexto())
        assert [r.codigo for r in resultado.reglas] == ["R1"]
        assert resultado.estado == "APROBADO"

    def test_subconjunto_rechazado(self, factura) -> None:
        motor = MotorReglas(reglas=[R1IntegridadCuit()])
        resultado = motor.evaluar(factura(cuit_emisor="30-12345678-9"), contexto())
        assert resultado.estado == "RECHAZADO"

    def test_subconjunto_con_r3(self, factura) -> None:
        motor = MotorReglas(reglas=[R3ConsistenciaMatematica()])
        resultado = motor.evaluar(factura(monto_total=Decimal("99000.00")), contexto())
        assert resultado.estado == "RECHAZADO"


class TestPuertos:
    def test_puertos_exponen_el_contrato(self) -> None:
        """Los puertos del dominio definen el contrato que implementa la infraestructura."""
        assert hasattr(ClockPort, "hoy")
        assert hasattr(PadronProveedoresPort, "buscar")


class TestRendimiento:
    def test_evaluacion_20_items_bajo_10ms(self, factura) -> None:
        """Referencia opcional (VERIFICATION-01 §1): < 10 ms sin I/O en el camino caliente."""
        items = [
            ItemFactura(
                descripcion=f"Ítem {i}",
                cantidad=Decimal("2"),
                precio_unitario=Decimal("1250.00"),
                subtotal=Decimal("2500.00"),
            )
            for i in range(20)
        ]
        f = factura(items=items, monto_total=Decimal("50000.00"))
        motor = MotorReglas()
        inicio = time.perf_counter()
        motor.evaluar(f, contexto())
        transcurrido_ms = (time.perf_counter() - inicio) * 1000
        assert transcurrido_ms < 10


class TestFacturaAConIvaDiscriminado:
    """Caso real (ADR-02-10): Factura A con IVA discriminado al pie.

    El extractor LLM devolvía `impuestos = 0` (casaba el campo con la fila
    'Importe Otros Tributos') y R3 rechazaba por el IVA discriminado. Con la
    semántica corregida (impuestos = suma de TODOS los impuestos discriminados),
    la misma auditoría queda APROBADO: 353.000 (neto) + 74.130 (IVA 21%)
    = 427.130. Fixture con fecha estática 2026-11-12: misma caducidad que
    ADR-02-06 (regenerar antes de ~2027-01-11).
    """

    RUTA = (
        Path(__file__).resolve().parents[2] / "data" / "fixtures" / "extraccion-factura-a-iva.json"
    )

    def _factura_a(self) -> FacturaExtraida:
        datos = json.loads(self.RUTA.read_text(encoding="utf-8"))
        return FacturaExtraida.model_validate(datos)  # misma validación del extractor

    def test_fixture_valida_contra_esquema(self) -> None:
        factura = self._factura_a()
        assert factura.impuestos == Decimal("74130.00")
        assert factura.monto_total == Decimal("427130.00")

    def test_r3_verde_con_iva_discriminado(self) -> None:
        """El fix del bug: R3 pasa con IVA discriminado (antes DISCREPANCIA_CONTABLE)."""
        resultado = R3ConsistenciaMatematica().evaluar(self._factura_a(), contexto())
        assert resultado.aprobado
        assert resultado.codigo_error is None

    def test_motor_completo_aprobado(self) -> None:
        austral = Proveedor(cuit="30712345671", razon_social="Comercial Austral SRL", activo=True)
        resultado = MotorReglas().evaluar(self._factura_a(), contexto(austral))
        assert resultado.estado == "APROBADO"
        assert all(r.aprobado for r in resultado.reglas)


class TestFacturaBTransparenciaFiscal:
    """Caso real (ADR-02-11): Factura B con recuado informativo Ley 27.743.

    El extractor LLM cargaba `impuestos = 107603.31` desde 'IVA Contenido
    (Ley 27.743)' — un desglose informativo YA INCLUIDO en el total y en los
    subtotales — y R3 rechazaba: 620.000 + 107.603,31 ≠ 620.000. Con la regla
    corregida (en B/C `impuestos = 0` salvo tributos que se adicionen), la
    auditoría queda APROBADO: ítems 620.000 (IVA incluido) + 0 = total
    620.000. Fixture con fecha estática 2026-11-13: caducidad R5
    ≈ 2027-01-12 (misma política que ADR-02-06).
    """

    RUTA = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "fixtures"
        / "extraccion-factura-b-transparencia.json"
    )

    def _factura_b(self) -> FacturaExtraida:
        datos = json.loads(self.RUTA.read_text(encoding="utf-8"))
        return FacturaExtraida.model_validate(datos)  # misma validación del extractor

    def test_fixture_valida_contra_esquema(self) -> None:
        factura = self._factura_b()
        assert factura.letra_comprobante == "B"
        assert factura.impuestos == Decimal("0.00")  # IVA Contenido 27.743 ignorado
        assert factura.monto_total == Decimal("620000.00")
        suma_items = sum((i.subtotal for i in factura.items), Decimal("0.00"))
        assert suma_items == Decimal("620000.00")

    def test_r3_verde_con_iva_contenido_ignorado(self) -> None:
        """El fix del bug: R3 pasa aunque el comprobante informe 'IVA Contenido'."""
        resultado = R3ConsistenciaMatematica().evaluar(self._factura_b(), contexto())
        assert resultado.aprobado
        assert resultado.codigo_error is None

    def test_motor_completo_aprobado(self) -> None:
        """Total > $500.000 → R4 exige OC (la fixture la trae: OC-2026-04712)."""
        ctx = ContextoAuditoria(hoy=date(2026, 11, 13), proveedor=ACTIVO)  # fecha del doc
        resultado = MotorReglas().evaluar(self._factura_b(), ctx)
        assert resultado.estado == "APROBADO"
        assert all(r.aprobado for r in resultado.reglas)


class TestFacturaAMixta:
    """Caso real (ADR-02-12): Factura A con alícuotas mixtas + percepción IIBB.

    El LLM recibía un único campo escalar `impuestos` y sumaba las 3 líneas
    del pie de memoria: devolvió 94.600 por 145.800 (error aritmético de
    $51.200) → R3 rechazaba DISCREPANCIA_CONTABLE. Con `detalle_impuestos`
    (una entrada por línea, extraída literal) y el recálculo en Python, la
    suma exacta es 75.600 + 46.200 + 24.000 = 145.800 y
    800.000 (neto) + 145.800 = 945.800 = total. Fixture con fecha estática
    2026-11-14: caducidad R5 ≈ 2027-01-13 (misma política que ADR-02-06).
    """

    RUTA = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "fixtures"
        / "extraccion-factura-a-mixta.json"
    )

    def _factura_mixta(self) -> FacturaExtraida:
        datos = json.loads(self.RUTA.read_text(encoding="utf-8"))
        return FacturaExtraida.model_validate(datos)  # misma validación del extractor

    def test_impuestos_recalculados_desde_detalle(self) -> None:
        """El fix del bug: aunque el modelo devuelva una suma errónea, Python
        recalcula `impuestos` como la suma exacta del detalle línea a línea."""
        datos = json.loads(self.RUTA.read_text(encoding="utf-8"))
        datos["impuestos"] = 94600.00  # la suma errónea del LLM reportada
        factura = FacturaExtraida.model_validate(datos)
        assert factura.impuestos == Decimal("145800.00")
        assert [(i.concepto, i.monto) for i in factura.detalle_impuestos] == [
            ("IVA 21%", Decimal("75600.00")),
            ("IVA 10,5%", Decimal("46200.00")),
            ("Percepción IIBB ARBA 3,00% (Otros Tributos)", Decimal("24000.00")),
        ]

    def test_numero_comprobante_con_punto_de_venta(self) -> None:
        """El PdV no se pierde: '00005-00019384', no solo '00019384'."""
        assert self._factura_mixta().numero_comprobante == "00005-00019384"

    def test_r3_verde_con_alicuotas_mixtas(self) -> None:
        """Neto $800.000 + IVA 21% $75.600 + IVA 10,5% $46.200 + Perc. IIBB $24.000 = $945.800."""
        resultado = R3ConsistenciaMatematica().evaluar(self._factura_mixta(), contexto())
        assert resultado.aprobado
        assert resultado.codigo_error is None

    def test_motor_completo_aprobado(self) -> None:
        """Total $945.800 > $500.000 → R4 exige OC (la fixture la trae)."""
        austral = Proveedor(cuit="30712345671", razon_social="Comercial Austral SRL", activo=True)
        ctx = ContextoAuditoria(hoy=date(2026, 11, 14), proveedor=austral)  # fecha del doc
        resultado = MotorReglas().evaluar(self._factura_mixta(), ctx)
        assert resultado.estado == "APROBADO"
        assert all(r.aprobado for r in resultado.reglas)

    def test_sin_detalle_impuestos_conserva_el_literal(self) -> None:
        """Retrocompatibilidad: sin `detalle_impuestos` (fixtures mock), `impuestos`
        conserva el valor extraído — el recálculo solo aplica con líneas presentes."""
        datos = json.loads(self.RUTA.read_text(encoding="utf-8"))
        datos.pop("detalle_impuestos")
        datos["impuestos"] = 74130.00  # valor literal de otra extracción
        factura = FacturaExtraida.model_validate(datos)
        assert factura.impuestos == Decimal("74130.00")
        assert factura.detalle_impuestos == []
