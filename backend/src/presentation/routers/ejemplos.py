"""Router: ejemplos pre-cargados para la demo (CU-05).

El catálogo es estático (matriz de TASKS-03 §Fase 1); los PDFs se leen de
`backend/data/ejemplos/`, generados por `scripts/generar_ejemplos.py`.
"""

from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.presentation.errores import ErrorHTTPTipado

router = APIRouter(prefix="/api/v1", tags=["ejemplos"])


@dataclass(frozen=True)
class Ejemplo:
    """Entrada del catálogo estático."""

    id: str
    nombre: str
    descripcion: str
    resultado_esperado: str
    archivo: str


CATALOGO: tuple[Ejemplo, ...] = (
    Ejemplo(
        id="ej-factura-aprobada",
        nombre="Factura Proveedor Homologado #001",
        descripcion=(
            "Flujo feliz: proveedor activo (CUIT 30-12345678-1), matemática consistente, "
            "OC-2026-0441 y emisión hoy−5."
        ),
        resultado_esperado="APROBADO",
        archivo="factura-aprobada-001.pdf",
    ),
    Ejemplo(
        id="ej-factura-desvio",
        nombre="Factura con desvío de monto",
        descripcion=(
            "Comercial Austral SRL: ítems + impuestos ($270.000) no coinciden con el total "
            "declarado ($285.000)."
        ),
        resultado_esperado="RECHAZADO (R3: DISCREPANCIA_CONTABLE)",
        archivo="factura-desvio-monto.pdf",
    ),
    Ejemplo(
        id="ej-monto-alto-sin-oc",
        nombre="Factura monto alto sin OC",
        descripcion=(
            "Servicios Técnicos SD S.A.: total de $650.000 supera el tope de $500.000 "
            "sin Orden de Compra."
        ),
        resultado_esperado="RECHAZADO (R4: FALTA_ORDEN_COMPRA)",
        archivo="factura-monto-alto-sin-oc.pdf",
    ),
)


class EjemploDTO(BaseModel):
    """Ítem del catálogo expuesto por la API."""

    id: str
    nombre: str
    descripcion: str
    resultado_esperado: str
    url_pdf: str


def _directorio(request: Request) -> Path:
    """Carpeta con los PDFs de ejemplo (configurada en `create_app`)."""
    return request.app.state.directorio_ejemplos


@router.get("/ejemplos", response_model=list[EjemploDTO])
def listar_ejemplos() -> list[EjemploDTO]:
    """Los 3 ejemplos con nombre, descripción, resultado esperado y URL del PDF."""
    return [
        EjemploDTO(
            id=ejemplo.id,
            nombre=ejemplo.nombre,
            descripcion=ejemplo.descripcion,
            resultado_esperado=ejemplo.resultado_esperado,
            url_pdf=f"/api/v1/ejemplos/{ejemplo.id}/pdf",
        )
        for ejemplo in CATALOGO
    ]


@router.get("/ejemplos/{id_ejemplo}/pdf")
def descargar_pdf(
    id_ejemplo: str,
    directorio: Annotated[Path, Depends(_directorio)],
) -> StreamingResponse:
    """Entrega el PDF crudo del ejemplo para el visor (iframe) del frontend."""
    ejemplo = next((item for item in CATALOGO if item.id == id_ejemplo), None)
    if ejemplo is None:
        raise ErrorHTTPTipado(
            404,
            "EJEMPLO_NO_ENCONTRADO",
            f"No existe el ejemplo '{id_ejemplo}'.",
        )
    ruta = directorio / ejemplo.archivo
    if not ruta.is_file():
        raise ErrorHTTPTipado(
            404,
            "EJEMPLO_NO_ENCONTRADO",
            f"El PDF del ejemplo '{id_ejemplo}' no está generado "
            "(ejecutar backend/scripts/generar_ejemplos.py).",
        )
    return StreamingResponse(
        BytesIO(ruta.read_bytes()),
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{ejemplo.archivo}"'},
    )
