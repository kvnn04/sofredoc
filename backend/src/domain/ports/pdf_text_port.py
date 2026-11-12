"""Puerto de salida: lectura de PDFs (la infraestructura lo implementa)."""

from typing import Protocol


class PdfTextPort(Protocol):
    """Contrato: bytes de un PDF → texto plano de todas sus páginas."""

    def extraer_texto(self, contenido: bytes) -> str: ...
