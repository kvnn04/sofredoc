"""Repositorio SQLite del historial de auditorías (DESIGN-03 §2, RN-3-03/05).

Implementa `AuditoriaRepositoryPort` con la stdlib (`sqlite3`, sin ORM): una
conexión compartida (`check_same_thread=False`), modo WAL y columnas de texto
serializadas en JSON. El esquema se aplica al inicializar (idempotente).
"""

import json
import sqlite3
import threading
from decimal import Decimal
from pathlib import Path

from src.domain.models import RegistroAuditoria, ReglaResultado

_ESQUEMA_SQL = Path(__file__).resolve().parent / "esquema.sql"

_INSERTAR = """
INSERT INTO comprobante_auditoria (
    id, nombre_archivo, estado_auditoria, cuit_emisor, monto_total,
    datos_extraidos, reglas_evaluadas, json_crudo_ia,
    tiempo_ejecucion_ms, latencia_extraccion_ms, latencia_reglas_ms, creado_en
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


class SqliteAuditoriaRepository:
    """Historial de auditorías sobre el archivo configurado por `DB_PATH`."""

    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()  # serializa el uso de la conexión compartida
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.executescript(_ESQUEMA_SQL.read_text(encoding="utf-8"))
        self._conn.commit()

    # ------------------------------------------------------------------ puerto
    def guardar(self, auditoria: RegistroAuditoria) -> None:
        """Persiste una auditoría (RN-3-03: antes de responder al cliente)."""
        with self._lock:
            self._conn.execute(_INSERTAR, self._parametros(auditoria))
            self._conn.commit()

    def listar(self, limit: int = 20, offset: int = 0) -> list[RegistroAuditoria]:
        """Listado paginado, el más nuevo primero (CU-04)."""
        with self._lock:
            filas = self._conn.execute(
                "SELECT * FROM comprobante_auditoria ORDER BY creado_en DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return [self._mapear(fila) for fila in filas]

    def obtener(self, id_auditoria: str) -> RegistroAuditoria | None:
        """Detalle completo por id; None si no existe (el router mapea a 404)."""
        with self._lock:
            fila = self._conn.execute(
                "SELECT * FROM comprobante_auditoria WHERE id = ?", (id_auditoria,)
            ).fetchone()
        return self._mapear(fila) if fila is not None else None

    def cerrar(self) -> None:
        """Cierra la conexión compartida (apagado de la app o teardown de tests)."""
        with self._lock:
            self._conn.close()

    # ------------------------------------------------------------------ helpers
    @staticmethod
    def _parametros(auditoria: RegistroAuditoria) -> tuple:
        """Modelo → fila: Decimal a REAL, dicts a JSON (`ensure_ascii=False`)."""
        datos = auditoria.datos_extraidos
        crudo = auditoria.json_crudo_ia
        return (
            auditoria.id,
            auditoria.nombre_archivo,
            auditoria.estado,
            auditoria.cuit_emisor,
            None if auditoria.monto_total is None else float(auditoria.monto_total),
            None if datos is None else json.dumps(datos, ensure_ascii=False),
            json.dumps(
                [regla.model_dump(mode="json") for regla in auditoria.reglas_evaluadas],
                ensure_ascii=False,
            ),
            None if crudo is None else json.dumps(crudo, ensure_ascii=False),
            auditoria.tiempo_ejecucion_ms,
            auditoria.latencia_extraccion_ms,
            auditoria.latencia_reglas_ms,
            auditoria.creado_en,
        )

    @staticmethod
    def _mapear(fila: sqlite3.Row) -> RegistroAuditoria:
        """Fila → modelo: REAL a Decimal, columnas JSON a dicts."""
        monto = fila["monto_total"]
        datos = fila["datos_extraidos"]
        crudo = fila["json_crudo_ia"]
        return RegistroAuditoria(
            id=fila["id"],
            nombre_archivo=fila["nombre_archivo"],
            estado=fila["estado_auditoria"],
            cuit_emisor=fila["cuit_emisor"],
            monto_total=None if monto is None else Decimal(str(monto)),
            datos_extraidos=(None if datos is None else json.loads(datos)),
            reglas_evaluadas=[
                ReglaResultado.model_validate(item) for item in json.loads(fila["reglas_evaluadas"])
            ],
            json_crudo_ia=None if crudo is None else json.loads(crudo),
            tiempo_ejecucion_ms=fila["tiempo_ejecucion_ms"],
            latencia_extraccion_ms=fila["latencia_extraccion_ms"],
            latencia_reglas_ms=fila["latencia_reglas_ms"],
            creado_en=fila["creado_en"],
        )
