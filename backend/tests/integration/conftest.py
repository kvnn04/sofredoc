"""Fixtures de integración: app FastAPI real sobre SQLite temporal.

Sin I/O externa: `EXTRACTOR_MODE=mock` (fixture local) o extractores falsificados
como stubs; la BD vive en `tmp_path`; el reloj es fijo para que R5 sea
determinista sin importar la fecha de corrida.
"""

from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.config import Settings
from src.domain.errors import ExtraccionFallidaError
from src.domain.models import ExtraccionResultado, FacturaExtraida, ItemFactura
from src.domain.ports.clock_port import ClockPort
from src.main import create_app

FECHA_FIJA = date(2026, 11, 12)  # 'hoy' determinista para R5
_RUTA_EJEMPLOS = Path(__file__).resolve().parents[2] / "data" / "ejemplos"


class RelojFijo:
    """Implementa `ClockPort` con fecha constante (R5 no depende del día real)."""

    def __init__(self, fecha: date) -> None:
        self._fecha = fecha

    def hoy(self) -> date:
        return self._fecha


class ExtractorQueFalla:
    """Stub del extractor: siempre falla tras el flujo de reintento (fila 7)."""

    def extraer(self, texto_pdf: str, nombre_archivo: str) -> ExtraccionResultado:
        raise ExtraccionFallidaError("El LLM no produjo un esquema válido tras el reintento.")


def _factura_monto_alto_sin_oc() -> ExtraccionResultado:
    """Fila 3 de la matriz: CUIT 20-12345678-6, 1 × $650.000, sin OC, fecha hoy−30."""
    factura = FacturaExtraida(
        tipo_comprobante="FACTURA",
        numero_comprobante="B-0002-00000789",
        cuit_emisor="20-12345678-6",
        razon_social="Servicios Técnicos SD S.A.",
        fecha_emision=FECHA_FIJA - timedelta(days=30),
        numero_orden_compra=None,
        items=[
            ItemFactura(
                descripcion="Equipamiento de rack para data center",
                cantidad=Decimal("1"),
                precio_unitario=Decimal("650000.00"),
                subtotal=Decimal("650000.00"),
            )
        ],
        impuestos=Decimal("0.00"),
        monto_total=Decimal("650000.00"),
    )
    return ExtraccionResultado(
        factura=factura,
        json_crudo_ia={"tipo_comprobante": "FACTURA", "cuit_emisor": "20-12345678-6"},
    )


def _factura_remito() -> ExtraccionResultado:
    """Fila extra: REMITO → R0 lo rechaza sin evaluar R1–R5 (decisión 2026-11-12)."""
    factura = FacturaExtraida(
        tipo_comprobante="REMITO",
        numero_comprobante="R-0001-00000100",
        cuit_emisor="30-12345678-1",
        razon_social="Distribuidora Andina S.A.",
        fecha_emision=FECHA_FIJA - timedelta(days=5),
        items=[
            ItemFactura(
                descripcion="Mercadería remitida",
                cantidad=Decimal("5"),
                precio_unitario=Decimal("2000.00"),
                subtotal=Decimal("10000.00"),
            )
        ],
        impuestos=Decimal("0.00"),
        monto_total=Decimal("10000.00"),
    )
    return ExtraccionResultado(factura=factura, json_crudo_ia={"tipo_comprobante": "REMITO"})


class ExtractorFijo:
    """Stub del extractor: devuelve siempre la extracción dada (como el mock)."""

    def __init__(self, resultado: ExtraccionResultado) -> None:
        self._resultado = resultado

    def extraer(self, texto_pdf: str, nombre_archivo: str) -> ExtraccionResultado:
        return self._resultado


def _pdf(textos: list[str]) -> bytes:
    """Arma un PDF de N páginas con un stream de texto por página (sin reportlab)."""
    total = len(textos)
    kids = " ".join(f"{4 + 2 * i} 0 R" for i in range(total))
    objetos: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {total} >>".encode(),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    for i, texto in enumerate(textos):
        objetos.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {5 + 2 * i} 0 R >>".encode()
        )
        stream = f"BT /F1 12 Tf 72 720 Td ({texto}) Tj ET".encode()
        objetos.append(f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream")

    salida = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for numero, cuerpo in enumerate(objetos, start=1):
        offsets.append(len(salida))
        salida += f"{numero} 0 obj\n".encode() + cuerpo + b"\nendobj\n"
    xref = len(salida)
    salida += f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n".encode()
    for desplazamiento in offsets:
        salida += f"{desplazamiento:010d} 00000 n \n".encode()
    salida += (
        f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    )
    return bytes(salida)


@pytest.fixture
def extractor_falla():
    """Extractor stub que siempre falla (fila 7: `502 EXTRACCION_FALLIDA`)."""
    return ExtractorQueFalla()


@pytest.fixture
def extractor_sin_oc():
    """Extractor stub con la fila 3 de la matriz: $650.000 sin OC → R4."""
    return ExtractorFijo(_factura_monto_alto_sin_oc())


@pytest.fixture
def extractor_remito():
    """Extractor stub con un REMITO → R0 rechaza sin evaluar R1–R5."""
    return ExtractorFijo(_factura_remito())


@pytest.fixture
def ruta_db(tmp_path) -> Path:
    """Archivo SQLite temporal exclusivo de cada test."""
    return tmp_path / "auditorias.db"


@pytest.fixture
def crear_cliente(ruta_db):
    """Factory de clientes de prueba con settings temporales y reloj fijo.

    Cierra las conexiones SQLite al terminar cada test (sin `ResourceWarning`).
    """
    repos = []

    def _crear(
        *,
        variante: str = "aprobada",
        extractor=None,
        reloj: ClockPort | None = None,
    ) -> TestClient:
        settings = Settings(
            db_path=str(ruta_db),
            extractor_mode="mock",
            mock_variant=variante,
            max_pdf_mb=5,
        )
        app = create_app(
            settings=settings,
            extractor=extractor,
            reloj=reloj or RelojFijo(FECHA_FIJA),
        )
        repos.append(app.state.auditorias_repo)
        return TestClient(app)

    yield _crear
    for repo in repos:
        repo.cerrar()


@pytest.fixture
def leer_ejemplo():
    """Lee un PDF de `backend/data/ejemplos/` (los generados por T-04)."""

    def _leer(nombre: str) -> bytes:
        return (_RUTA_EJEMPLOS / nombre).read_bytes()

    return _leer


@pytest.fixture
def pdf_en_memoria():
    """Factory de PDFs mínimos en memoria (texto por página, sin dependencias)."""
    return _pdf


@pytest.fixture
def fila_sqlite(ruta_db):
    """Consulta directa al SQLite temporal (verifica la fila persistida)."""

    def _consultar(sql: str, params: tuple = ()):
        import sqlite3

        conexion = sqlite3.connect(ruta_db)
        try:
            return conexion.execute(sql, params).fetchone()
        finally:
            conexion.close()

    return _consultar
