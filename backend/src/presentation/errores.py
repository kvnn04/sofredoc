"""Mapeo de errores → respuestas HTTP tipadas (DESIGN-03 §3, RN-3-02).

Los códigos de error van `MAYUSCULAS_CON_GUIONES_BAJOS`, sin prefijos HTTP, y
el cuerpo siempre es `{"error": {"codigo": ..., "mensaje": ...}}`. Un resultado
de negocio RECHAZADO nunca pasa por acá: es un `200 OK` del flujo normal.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.errors import ErrorTipificado

# Estado HTTP para cada error tipificado que levantan los adaptadores (MOD-02).
_STATUS_POR_CODIGO = {
    "ARCHIVO_MUY_GRANDE": 413,
    "PDF_INVALIDO": 422,
    "PDF_SIN_TEXTO": 422,
    "EXTRACCION_FALLIDA": 502,
}


class ErrorHTTPTipado(Exception):
    """Error de contrato que levanta un router y el handler serializa con el cuerpo pactado."""

    def __init__(self, status_code: int, codigo: str, mensaje: str) -> None:
        super().__init__(mensaje)
        self.status_code = status_code
        self.codigo = codigo
        self.mensaje = mensaje


def _cuerpo(codigo: str, mensaje: str) -> dict:
    return {"error": {"codigo": codigo, "mensaje": mensaje}}


def registrar_handlers(app: FastAPI) -> None:
    """Registra los handlers de errores tipados sobre la app."""

    @app.exception_handler(ErrorTipificado)
    async def _mapear_error_dominio(request: Request, exc: ErrorTipificado) -> JSONResponse:
        """Errores de ingesta/extracción (PDF_INVALIDO, PDF_SIN_TEXTO, EXTRACCION_FALLIDA...)."""
        status = _STATUS_POR_CODIGO.get(exc.codigo, 500)
        return JSONResponse(
            status_code=status,
            content=_cuerpo(exc.codigo, exc.mensaje),
        )

    @app.exception_handler(ErrorHTTPTipado)
    async def _mapear_error_http(request: Request, exc: ErrorHTTPTipado) -> JSONResponse:
        """Errores de contrato levantados en los routers (413/422/404...)."""
        return JSONResponse(
            status_code=exc.status_code,
            content=_cuerpo(exc.codigo, exc.mensaje),
        )
