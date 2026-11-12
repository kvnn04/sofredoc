"""Router: `POST /api/v1/auditar` (CU-01/02/03).

Validaciones de contrato (tamaño 413 y MIME/extensión 422) antes del caso de
uso; el resultado de negocio —aprobado o rechazado— responde `200` (RN-3-02).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Request, UploadFile

from src.application.auditar_comprobante import AuditarComprobanteUseCase
from src.config import Settings
from src.presentation.dtos import RegistroAuditoriaDTO
from src.presentation.errores import ErrorHTTPTipado

router = APIRouter(prefix="/api/v1", tags=["auditoría"])


def _use_case(request: Request) -> AuditarComprobanteUseCase:
    """Caso de uso construido en `create_app` (inyección vía app.state)."""
    return request.app.state.auditar_use_case


def _settings(request: Request) -> Settings:
    return request.app.state.settings


def _es_pdf(nombre: str, content_type: str | None) -> bool:
    """RN-3-01: vale content-type `application/pdf` o extensión `.pdf`."""
    if content_type == "application/pdf":
        return True
    return nombre.lower().endswith(".pdf")


@router.post("/auditar", response_model=RegistroAuditoriaDTO)
async def auditar(
    file: UploadFile,
    use_case: Annotated[AuditarComprobanteUseCase, Depends(_use_case)],
    settings: Annotated[Settings, Depends(_settings)],
) -> RegistroAuditoriaDTO:
    """Audita un PDF (≤ 5 MB) y devuelve datos + semáforo + trazabilidad en `200`."""
    contenido = await file.read()
    nombre = file.filename or "comprobante.pdf"

    tope = settings.max_pdf_mb * 1024 * 1024
    if len(contenido) > tope:
        raise ErrorHTTPTipado(
            413,
            "ARCHIVO_MUY_GRANDE",
            f"El archivo supera el tope de {settings.max_pdf_mb} MB.",
        )
    if not _es_pdf(nombre, file.content_type):
        raise ErrorHTTPTipado(
            422,
            "PDF_INVALIDO",
            "El archivo debe ser un PDF (extensión .pdf o content-type application/pdf).",
        )

    registro = use_case.ejecutar(contenido, nombre)
    return RegistroAuditoriaDTO.desde_registro(registro)
