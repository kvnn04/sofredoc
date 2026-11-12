"""Router: historial de auditorías persistidas (CU-04, RN-3-04).

El listado es paginado (limit/offset, el más nuevo primero) y omite el JSON
crudo del LLM por peso; el detalle completo está en `GET /historial/{id}`.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from src.domain.ports.auditoria_repository_port import AuditoriaRepositoryPort
from src.presentation.dtos import RegistroAuditoriaDTO, ResumenAuditoriaDTO
from src.presentation.errores import ErrorHTTPTipado

router = APIRouter(prefix="/api/v1", tags=["historial"])


def _repo(request: Request) -> AuditoriaRepositoryPort:
    """Repositorio construido en `create_app` (inyección vía app.state)."""
    return request.app.state.auditorias_repo


@router.get("/historial", response_model=list[ResumenAuditoriaDTO])
def listar_historial(
    repo: Annotated[AuditoriaRepositoryPort, Depends(_repo)],
    limit: Annotated[int, Query(ge=1)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[ResumenAuditoriaDTO]:
    """Listado paginado ordenado por `creado_en` descendente, sin `json_crudo_ia`."""
    registros = repo.listar(limit=limit, offset=offset)
    return [ResumenAuditoriaDTO.desde_registro(registro) for registro in registros]


@router.get("/historial/{id_auditoria}", response_model=RegistroAuditoriaDTO)
def detalle_auditoria(
    id_auditoria: str,
    repo: Annotated[AuditoriaRepositoryPort, Depends(_repo)],
) -> RegistroAuditoriaDTO:
    """Detalle completo de una auditoría del historial (incluye JSON crudo)."""
    registro = repo.obtener(id_auditoria)
    if registro is None:
        raise ErrorHTTPTipado(
            404,
            "AUDITORIA_NO_ENCONTRADA",
            f"No existe la auditoría '{id_auditoria}'.",
        )
    return RegistroAuditoriaDTO.desde_registro(registro)
