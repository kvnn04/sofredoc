"""Pruebas del MotorReglas: admisión R0, estado global, fallos múltiples e inyección (T-16)."""

import time
from datetime import date, timedelta
from decimal import Decimal

from src.domain.models import ItemFactura
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
