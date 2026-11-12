"""Puerto de salida: extracción de documentos con IA (la infraestructura lo implementa)."""

from typing import Protocol

from src.domain.models import ExtraccionResultado


class DocumentExtractorPort(Protocol):
    """Contrato: texto del PDF + nombre de archivo → extracción validada.

    La IA solo extrae (RN-2-06): devuelve el objeto tipado tal cual el
    documento; decidir la validez es trabajo del motor de reglas (MOD-01).
    """

    def extraer(self, texto_pdf: str, nombre_archivo: str) -> ExtraccionResultado: ...
