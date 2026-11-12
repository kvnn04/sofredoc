"""Puerto de salida: repositorio del historial de auditorías (CU-04, RN-3-04)."""

from typing import Protocol

from src.domain.models import RegistroAuditoria


class AuditoriaRepositoryPort(Protocol):
    """Contrato de persistencia de auditorías: guardar, listar paginado, obtener.

    El historial es de solo lectura vía API (RN-3-04): el puerto no expone
    borrado ni actualización. La infraestructura (SQLite) lo implementa.
    """

    def guardar(self, auditoria: RegistroAuditoria) -> None: ...

    def listar(self, limit: int = 20, offset: int = 0) -> list[RegistroAuditoria]: ...

    def obtener(self, id_auditoria: str) -> RegistroAuditoria | None: ...
