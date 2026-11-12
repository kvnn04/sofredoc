"""Genera los 3 PDFs de ejemplo de la demo (T-04: matriz de TASKS-03 §Fase 1).

Uso (desde `backend/`):  python scripts/generar_ejemplos.py

Los archivos quedan en `backend/data/ejemplos/` y son los que sirven los
endpoints `/api/v1/ejemplos*` (CU-05). Los montos y CUITs son la matriz de
verdad: con `EXTRACTOR_MODE=llm` la extracción debe reproducirlos y las reglas
R1–R5 producir el resultado esperado de cada ejemplo. Las fechas son relativas
al día de generación (hoy −5/−20/−30, zona America/Argentina/Buenos_Aires):
re-ejecutar el script si la demo envejece más de 60 días (R5).
"""

import sys
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

_RUTA_BACKEND = Path(__file__).resolve().parent.parent  # backend/
sys.path.insert(0, str(_RUTA_BACKEND))  # permite `python scripts/generar_ejemplos.py`

from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402

from src.domain.rules.base import formato_ars  # noqa: E402  (mismo formato que las reglas)
from src.infrastructure.clock import ZONA_NEGOCIO  # noqa: E402

_DIRECTORIO = _RUTA_BACKEND / "data" / "ejemplos"


def _monto(valor: str) -> str:
    """Formatea un monto es-AR ($175.000,00) igual que los mensajes de reglas."""
    return formato_ars(Decimal(valor))


def _lineas_aprobada(fecha: str) -> list[str]:
    """CU-01: CUIT activo, matemática consistente, OC presente, fecha hoy−5."""
    return [
        "Distribuidora Andina S.A.",
        "CUIT: 30-12345678-1",
        "Tipo de comprobante: FACTURA",
        "N° de comprobante: A-0001-00000123",
        f"Fecha de emisión: {fecha}",
        "Orden de compra: OC-2026-0441",
        "",
        "Detalle de ítems:",
        (
            "Servicio de instalación torre 4G | Cantidad: 2 | "
            f"Precio unitario: {_monto('175000.00')} | Subtotal: {_monto('350000.00')}"
        ),
        "",
        "Subtotal (sin impuestos): $350.000,00",
        f"Impuestos: {_monto('34000.00')}",
        f"TOTAL: {_monto('384000.00')}",
    ]


def _lineas_desvio(fecha: str) -> list[str]:
    """CU-02 (R3): suma de ítems + impuestos ($270.000) ≠ total declarado ($285.000)."""
    return [
        "Comercial Austral SRL",
        "CUIT: 30-71234567-1",
        "Tipo de comprobante: FACTURA",
        "N° de comprobante: B-0002-00000456",
        f"Fecha de emisión: {fecha}",
        "",
        "Detalle de ítems:",
        (
            "Mantenimiento anual de servidores | Cantidad: 1 | "
            f"Precio unitario: {_monto('200000.00')} | Subtotal: {_monto('200000.00')}"
        ),
        (
            "Licencias de software | Cantidad: 3 | "
            f"Precio unitario: {_monto('15000.00')} | Subtotal: {_monto('45000.00')}"
        ),
        "",
        "Subtotal (sin impuestos): $270.000,00",
        f"Impuestos: {_monto('25000.00')}",
        f"TOTAL: {_monto('285000.00')}",
        "",
        "(El comprobante no informa Orden de Compra.)",
    ]


def _lineas_monto_alto(fecha: str) -> list[str]:
    """CU-02 (R4): $650.000 > tope $500.000 sin Orden de Compra."""
    return [
        "Servicios Técnicos SD S.A.",
        "CUIT: 20-12345678-6",
        "Tipo de comprobante: FACTURA",
        "N° de comprobante: B-0002-00000789",
        f"Fecha de emisión: {fecha}",
        "",
        "Detalle de ítems:",
        (
            "Equipamiento de rack para data center | Cantidad: 1 | "
            f"Precio unitario: {_monto('650000.00')} | Subtotal: {_monto('650000.00')}"
        ),
        "",
        "Subtotal (sin impuestos): $650.000,00",
        f"Impuestos: {_monto('0.00')}",
        f"TOTAL: {_monto('650000.00')}",
        "",
        "(El comprobante no informa Orden de Compra.)",
    ]


def _generar(nombre: str, lineas: list[str]) -> Path:
    """Escribe un PDF de una página con el texto del comprobante."""
    ruta = _DIRECTORIO / nombre
    documento = canvas.Canvas(str(ruta), pagesize=A4)
    documento.setFont("Helvetica", 11)
    y = 800
    for linea in lineas:
        documento.drawString(72, y, linea)
        y -= 20
    documento.save()
    return ruta


def main() -> None:
    """Genera los 3 PDFs con fechas relativas al día de hoy (TZ de negocio)."""
    hoy = datetime.now(tz=ZONA_NEGOCIO).date()
    _DIRECTORIO.mkdir(parents=True, exist_ok=True)
    ejemplos = [
        ("factura-aprobada-001.pdf", _lineas_aprobada((hoy - timedelta(days=5)).isoformat())),
        ("factura-desvio-monto.pdf", _lineas_desvio((hoy - timedelta(days=20)).isoformat())),
        (
            "factura-monto-alto-sin-oc.pdf",
            _lineas_monto_alto((hoy - timedelta(days=30)).isoformat()),
        ),
    ]
    for nombre, lineas in ejemplos:
        ruta = _generar(nombre, lineas)
        print(f"OK {ruta.relative_to(_RUTA_BACKEND)} ({ruta.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
