"""Genera los PDFs fixture del E2E Playwright (MOD-05, escenarios extendidos).

Uso (desde `backend/`):  python scripts/generar_fixtures_e2e.py

Los archivos quedan en `qa/e2e/fixtures/` y son commiteados (los tests los leen
con `readFileSync`, igual que los ejemplos de `backend/data/ejemplos/`):

- `remito-transporte-2026.pdf`: 1 página con capa de texto y "remito" en el
  nombre → el MockExtractor la resuelve con la fixture REMITO (ADR-05-08) y el
  motor aplica la admisión R0 (REMITO_NO_AUDITABLE).
- `pdf-escaneado-grafico.pdf`: 1 página solo-gráficos (sin capa de texto) →
  `PDF_SIN_TEXTO` (422) antes de llegar al extractor/LLM.
- `factura-11-paginas.pdf`: 11 páginas con texto → `PDF_INVALIDO` (422) por
  superar el tope de 10 páginas, validado en el backend (RN-2-01).

No dependen de fechas: el remito y la factura multipágina solo necesitan una
capa de texto válida (el contenido no se usa en modo mock).
"""

import sys
from pathlib import Path

_RUTA_BACKEND = Path(__file__).resolve().parent.parent  # backend/
sys.path.insert(0, str(_RUTA_BACKEND))  # permite `python scripts/generar_fixtures_e2e.py`

from reportlab.lib.pagesizes import A4  # noqa: E402
from reportlab.pdfgen import canvas  # noqa: E402

_DESTINO = _RUTA_BACKEND.parent / "qa" / "e2e" / "fixtures"


def _generar(nombre: str, lineas: list[str], paginas: int = 1) -> Path:
    """Escribe un PDF de N páginas; `lineas` se reparte en la primera página."""
    ruta = _DESTINO / nombre
    documento = canvas.Canvas(str(ruta), pagesize=A4)
    documento.setFont("Helvetica", 11)
    y = 800
    for linea in lineas:
        documento.drawString(72, y, linea)
        y -= 20
    for pagina in range(1, paginas):
        documento.showPage()
        documento.setFont("Helvetica", 11)
        documento.drawString(72, 800, f"Factura pagina {pagina + 1} de {paginas} (continuacion)")
    documento.save()
    return ruta


def main() -> None:
    """Genera los 3 PDFs fixture del E2E en qa/e2e/fixtures/."""
    _DESTINO.mkdir(parents=True, exist_ok=True)
    fixture_remito = _generar(
        "remito-transporte-2026.pdf",
        [
            "Comercial Austral SRL",
            "CUIT: 30-71234567-1",
            "Tipo de comprobante: REMITO",
            "N° de remito: R-0001-00000999",
            "Fecha de emisión: 2026-11-07",
            "",
            "Detalle de mercadería:",
            "Transferencia de mercadería (12 cajas) | Cantidad: 12 | "
            "Precio unitario: $1.500,00 | Subtotal: $18.000,00",
            "",
            "TOTAL: $18.000,00",
        ],
    )
    # Escaneado: solo un rectángulo gris (simulación de scan), cero operadores de texto.
    ruta_escaneado = _DESTINO / "pdf-escaneado-grafico.pdf"
    documento = canvas.Canvas(str(ruta_escaneado), pagesize=A4)
    documento.setFillColorRGB(0.92, 0.92, 0.92)
    documento.rect(0, 0, 595, 842, fill=1, stroke=0)
    documento.showPage()
    documento.save()
    fixture_11_paginas = _generar(
        "factura-11-paginas.pdf",
        [
            "Servicios Técnicos SD S.A.",
            "CUIT: 20-12345678-6",
            "Tipo de comprobante: FACTURA",
            "N° de comprobante: B-0002-00001234",
            "Fecha de emisión: 2026-11-07",
            "",
            "(Documento de 11 páginas: supera el tope de 10 del MVP.)",
        ],
        paginas=11,
    )
    for ruta in (fixture_remito, ruta_escaneado, fixture_11_paginas):
        print(f"OK {ruta.relative_to(_RUTA_BACKEND.parent)} ({ruta.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
