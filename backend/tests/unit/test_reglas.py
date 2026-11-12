"""Pruebas de reglas R1–R5 con la matriz de casos borde (T-15, VERIFICATION-01 §1)."""

from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.domain.ports.padron_port import Proveedor
from src.domain.rules.base import ContextoAuditoria
from src.domain.rules.r1_cuit import R1IntegridadCuit
from src.domain.rules.r2_proveedor import R2ProveedorHabilitado
from src.domain.rules.r3_matematica import R3ConsistenciaMatematica
from src.domain.rules.r4_orden_compra import R4TopeSinOrdenCompra
from src.domain.rules.r5_vigencia import R5VigenciaComprobante

HOY = date(2026, 11, 12)
ACTIVO = Proveedor(cuit="30123456781", razon_social="Distribuidora Andina S.A.", activo=True)
INACTIVO = Proveedor(cuit="20876543215", razon_social="Proveedor Baja SRL", activo=False)


class TestR1IntegridadCuit:
    regla = R1IntegridadCuit()

    def test_cuit_valido_aprueba(self, factura) -> None:
        r = self.regla.evaluar(factura(), ContextoAuditoria(hoy=HOY))
        assert r.aprobado
        assert r.codigo == "R1"
        assert r.codigo_error is None

    @pytest.mark.parametrize("cuit", ["30-12345678-9", "30-12345678", "30-1234567A-1", ""])
    def test_cuit_invalido_rechaza(self, factura, cuit: str) -> None:
        r = self.regla.evaluar(factura(cuit_emisor=cuit), ContextoAuditoria(hoy=HOY))
        assert not r.aprobado
        assert r.codigo_error == "ERROR_CUIT_INVALIDO"


class TestR2ProveedorHabilitado:
    regla = R2ProveedorHabilitado()

    def test_proveedor_activo_aprueba(self, factura) -> None:
        r = self.regla.evaluar(factura(), ContextoAuditoria(hoy=HOY, proveedor=ACTIVO))
        assert r.aprobado
        assert r.codigo_error is None

    def test_proveedor_ausente_rechaza(self, factura) -> None:
        r = self.regla.evaluar(factura(), ContextoAuditoria(hoy=HOY, proveedor=None))
        assert not r.aprobado
        assert r.codigo_error == "PROVEEDOR_NO_REGISTRADO"

    def test_proveedor_inactivo_rechaza(self, factura) -> None:
        r = self.regla.evaluar(factura(), ContextoAuditoria(hoy=HOY, proveedor=INACTIVO))
        assert not r.aprobado
        assert r.codigo_error == "PROVEEDOR_NO_REGISTRADO"


class TestR3ConsistenciaMatematica:
    regla = R3ConsistenciaMatematica()

    def test_consistente_aprueba(self, factura) -> None:
        r = self.regla.evaluar(factura(), ContextoAuditoria(hoy=HOY))
        assert r.aprobado
        assert r.codigo_error is None

    def test_desvio_exactamente_un_peso_aprueba(self, factura) -> None:
        """Fila 11: calculado $25.001,00 vs declarado $25.000,00 → dentro de tolerancia."""
        r = self.regla.evaluar(factura(impuestos=Decimal("1.00")), ContextoAuditoria(hoy=HOY))
        assert r.aprobado

    def test_desvio_un_peso_uno_rechaza(self, factura) -> None:
        """Fila 12: desvío $1.01 → fuera de tolerancia, con detalles."""
        r = self.regla.evaluar(factura(impuestos=Decimal("1.01")), ContextoAuditoria(hoy=HOY))
        assert not r.aprobado
        assert r.codigo_error == "DISCREPANCIA_CONTABLE"
        assert r.detalles == {"calculado": "25001.01", "declarado": "25000.00"}
        assert "$25.001,01" in r.mensaje and "$25.000,00" in r.mensaje

    def test_desvio_negativo_rechaza_con_detalles(self, factura) -> None:
        """Fila 13: total menor que la suma; detalles con ambos montos."""
        r = self.regla.evaluar(factura(monto_total=Decimal("20000.00")), ContextoAuditoria(hoy=HOY))
        assert not r.aprobado
        assert r.codigo_error == "DISCREPANCIA_CONTABLE"
        assert r.detalles == {"calculado": "25000.00", "declarado": "20000.00"}

    def test_calculado_negativo_formatea_con_signo(self, factura) -> None:
        """Impuestos negativos grandes: el monto calculado se muestra como -$5.000,00."""
        r = self.regla.evaluar(factura(impuestos=Decimal("-30000")), ContextoAuditoria(hoy=HOY))
        assert not r.aprobado
        assert "-$5.000,00" in r.mensaje
        assert r.detalles == {"calculado": "-5000.00", "declarado": "25000.00"}


class TestR4TopeSinOrdenCompra:
    regla = R4TopeSinOrdenCompra()

    def test_monto_bajo_tope_con_oc_aprueba(self, factura) -> None:
        r = self.regla.evaluar(factura(), ContextoAuditoria(hoy=HOY))
        assert r.aprobado
        assert r.mensaje == "OC presente."

    def test_monto_bajo_tope_sin_oc_aprueba(self, factura) -> None:
        r = self.regla.evaluar(factura(numero_orden_compra=None), ContextoAuditoria(hoy=HOY))
        assert r.aprobado
        assert r.mensaje == "Monto bajo el tope, OC no requerida."

    def test_tope_exacto_sin_oc_aprueba(self, factura) -> None:
        """Fila 14: $500.000,00 no supera el tope (estricto >)."""
        f = factura(monto_total=Decimal("500000.00"), numero_orden_compra=None)
        r = self.regla.evaluar(f, ContextoAuditoria(hoy=HOY))
        assert r.aprobado
        assert r.codigo_error is None

    def test_tope_excedido_un_centavo_sin_oc_rechaza(self, factura) -> None:
        """Fila 15: $500.000,01 ya exige OC."""
        f = factura(monto_total=Decimal("500000.01"), numero_orden_compra=None)
        r = self.regla.evaluar(f, ContextoAuditoria(hoy=HOY))
        assert not r.aprobado
        assert r.codigo_error == "FALTA_ORDEN_COMPRA"
        assert "$500.000,01" in r.mensaje and "$500.000,00" in r.mensaje

    def test_monto_alto_con_oc_aprueba(self, factura) -> None:
        """Fila 16: $725.000 con OC-2026-001 aprueba."""
        f = factura(monto_total=Decimal("725000.00"), numero_orden_compra="OC-2026-001")
        r = self.regla.evaluar(f, ContextoAuditoria(hoy=HOY))
        assert r.aprobado
        assert r.mensaje == "OC presente."

    def test_oc_solo_espacios_rechaza(self, factura) -> None:
        """Fila 17: OC en blanco no cuenta como presente con tope excedido."""
        f = factura(monto_total=Decimal("725000.00"), numero_orden_compra="   ")
        r = self.regla.evaluar(f, ContextoAuditoria(hoy=HOY))
        assert not r.aprobado
        assert r.codigo_error == "FALTA_ORDEN_COMPRA"


class TestR5VigenciaComprobante:
    regla = R5VigenciaComprobante()

    def test_emitida_hoy_aprueba(self, factura) -> None:
        """Fila 18: emitida hoy = válida."""
        r = self.regla.evaluar(factura(fecha_emision=HOY), ContextoAuditoria(hoy=HOY))
        assert r.aprobado
        assert r.codigo_error is None

    def test_sesenta_dias_aprueba(self, factura) -> None:
        """Fila 19: hoy − fecha == 60 días aprueba (no supera el tope)."""
        f = factura(fecha_emision=HOY - timedelta(days=60))
        r = self.regla.evaluar(f, ContextoAuditoria(hoy=HOY))
        assert r.aprobado

    def test_sesenta_y_un_dias_rechaza(self, factura) -> None:
        """Fila 20: a 61 días vence, con conteo en el mensaje."""
        f = factura(fecha_emision=HOY - timedelta(days=61))
        r = self.regla.evaluar(f, ContextoAuditoria(hoy=HOY))
        assert not r.aprobado
        assert r.codigo_error == "COMPROBANTE_VENCIDO"
        assert "vencido" in r.mensaje and "61" in r.mensaje

    def test_fecha_futura_rechaza(self, factura) -> None:
        """Fila 21: fecha futura rechaza, distinguiéndose del caso vencido (CU-05)."""
        f = factura(fecha_emision=HOY + timedelta(days=1))
        r = self.regla.evaluar(f, ContextoAuditoria(hoy=HOY))
        assert not r.aprobado
        assert r.codigo_error == "COMPROBANTE_VENCIDO"
        assert "futura" in r.mensaje.lower()
