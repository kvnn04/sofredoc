"""Fixtures compartidos de las pruebas unitarias (dominio y motor de reglas)."""

from datetime import date
from decimal import Decimal

import pytest

from src.domain.models import FacturaExtraida, ItemFactura

FECHA_BASE = date(2026, 11, 1)


@pytest.fixture
def factura():
    """Factory: `FacturaExtraida` válida para las 5 reglas; overrides vía kwargs."""

    def _factory(**overrides) -> FacturaExtraida:
        valores = {
            "tipo_comprobante": "FACTURA",
            "numero_comprobante": "0001-00001234",
            "cuit_emisor": "30-12345678-1",
            "razon_social": "Distribuidora Andina S.A.",
            "fecha_emision": FECHA_BASE,
            "numero_orden_compra": "OC-2026-001",
            "items": [
                ItemFactura(
                    descripcion="Resma papel A4",
                    cantidad=Decimal("10"),
                    precio_unitario=Decimal("2500.00"),
                    subtotal=Decimal("25000.00"),
                )
            ],
            "impuestos": Decimal("0.00"),
            "monto_total": Decimal("25000.00"),
        }
        valores.update(overrides)
        return FacturaExtraida(**valores)

    return _factory
