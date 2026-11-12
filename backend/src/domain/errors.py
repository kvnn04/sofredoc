"""Taxonomía de errores tipificados de ingesta/extracción (DESIGN-02 §5).

Excepciones puras de Python: las levantan los adaptadores de infraestructura
(pypdf, SDK LLM) y las capas `application/` y `presentation/` las capturan para
mapearlas a los códigos expuestos (`PDF_INVALIDO`, `PDF_SIN_TEXTO`,
`EXTRACCION_FALLIDA`). Viven en `domain/` para no acoplar el caso de uso a
adaptadores concretos.
"""


class ErrorTipificado(Exception):
    """Error con código de negocio estable (MOD-03 lo mapea a HTTP)."""

    codigo = "ERROR_INTERNO"

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class PdfInvalidoError(ErrorTipificado):
    """Bytes no parseables por pypdf o PDF cifrado sin password."""

    codigo = "PDF_INVALIDO"


class PdfDemasiadasPaginasError(PdfInvalidoError):
    """PDF que supera el límite de 10 páginas (RN-2-07).

    Comparte código con `PdfInvalidoError` pero el mensaje señala el límite.
    """

    codigo = "PDF_INVALIDO"


class PdfSinTextoError(ErrorTipificado):
    """Texto extraído < 20 caracteres significativos: PDF escaneado (RN-2-02)."""

    codigo = "PDF_SIN_TEXTO"


class ExtraccionFallidaError(ErrorTipificado):
    """ValidationError tras 1 reintento o error del proveedor LLM (RN-2-03)."""

    codigo = "EXTRACCION_FALLIDA"
