"""Adapter pypdf: bytes de PDF → texto plano (DESIGN-02 §1, RN-2-02 y RN-2-07)."""

import logging
from io import BytesIO

from pypdf import PdfReader

from src.domain.errors import (
    PdfDemasiadasPaginasError,
    PdfInvalidoError,
    PdfSinTextoError,
)

logger = logging.getLogger(__name__)

MAX_PAGINAS = 10  # RN-2-07: límite de páginas por comprobante
UMBRAL_SIN_TEXTO = 20  # RN-2-02: menos caracteres significativos => escaneo


class PypdfTextExtractor:
    """Extrae y concatena el texto de todas las páginas de un PDF digital."""

    def extraer_texto(self, contenido: bytes) -> str:
        try:
            lector = PdfReader(BytesIO(contenido))
        except Exception as exc:
            raise PdfInvalidoError(f"El archivo no es un PDF parseable: {exc}") from exc

        if lector.is_encrypted:
            raise PdfInvalidoError("El PDF está cifrado y no se recibió password.")

        try:
            total = len(lector.pages)
        except Exception as exc:
            raise PdfInvalidoError(f"PDF ilegible: {exc}") from exc

        if total > MAX_PAGINAS:
            raise PdfDemasiadasPaginasError(
                f"El PDF tiene {total} páginas y el límite es {MAX_PAGINAS} (RN-2-07)."
            )

        try:
            texto = "\n".join(pagina.extract_text() or "" for pagina in lector.pages)
        except Exception as exc:
            raise PdfInvalidoError(f"No se pudo extraer el texto del PDF: {exc}") from exc

        significativos = "".join(texto.split())
        if len(significativos) < UMBRAL_SIN_TEXTO:
            logger.warning(
                "PDF sin capa de texto (%d caracteres significativos).", len(significativos)
            )
            raise PdfSinTextoError(
                "El PDF parece escaneado (sin capa de texto); el MVP no incluye OCR."
            )

        return texto
