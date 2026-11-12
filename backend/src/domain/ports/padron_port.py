"""Puerto de salida: padrón de proveedores (la infraestructura lo implementa)."""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Proveedor:
    """Registro del padrón simulado (T-11: backend/data/proveedores.json)."""

    cuit: str
    razon_social: str
    activo: bool


class PadronProveedoresPort(Protocol):
    """Contrato de consulta de proveedores por CUIT normalizado."""

    def buscar(self, cuit: str) -> Proveedor | None: ...
