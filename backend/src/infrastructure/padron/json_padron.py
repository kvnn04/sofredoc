"""Adaptador de padrón: proveedores desde backend/data/proveedores.json (cache en memoria)."""

import json
import logging
from pathlib import Path

from src.domain.ports.padron_port import Proveedor

logger = logging.getLogger(__name__)


class JsonPadronProveedores:
    """Implementa `PadronProveedoresPort`: carga el JSON una sola vez y expone `buscar`."""

    def __init__(self, ruta: Path) -> None:
        self._ruta = ruta
        self._cache: dict[str, Proveedor] | None = None

    def buscar(self, cuit: str) -> Proveedor | None:
        """Busca por CUIT normalizado (sin guiones); devuelve None si no existe."""
        return self._cargar().get(cuit.strip().replace("-", ""))

    def _cargar(self) -> dict[str, Proveedor]:
        if self._cache is None:
            self._cache = self._leer_json()
        return self._cache

    def _leer_json(self) -> dict[str, Proveedor]:
        if not self._ruta.exists():
            logger.warning(
                "Padrón de proveedores no encontrado en %s; se considera vacío.", self._ruta
            )
            return {}
        registros = json.loads(self._ruta.read_text(encoding="utf-8"))
        return {
            registro["cuit"].replace("-", ""): Proveedor(
                cuit=registro["cuit"],
                razon_social=registro["razon_social"],
                activo=registro["activo"],
            )
            for registro in registros
        }
