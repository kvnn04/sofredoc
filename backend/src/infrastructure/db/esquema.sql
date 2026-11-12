-- Esquema del historial de auditorías (DESIGN-03 §2).
-- Se aplica al arranque de la app: idempotente (IF NOT EXISTS), sin migraciones.

CREATE TABLE IF NOT EXISTS comprobante_auditoria (
    id TEXT PRIMARY KEY,                        -- aud_xxxxxxxx
    nombre_archivo TEXT NOT NULL,
    estado_auditoria TEXT NOT NULL,             -- APROBADO | RECHAZADO | ERROR_EXTRACCION
    cuit_emisor TEXT,                           -- NULL si la extracción falló
    monto_total REAL,                           -- NULL si la extracción falló
    datos_extraidos TEXT,                       -- JSON (FacturaExtraida) o NULL
    reglas_evaluadas TEXT NOT NULL,             -- JSON ([ReglaResultado]) — en ERROR_EXTRACCION: []
    json_crudo_ia TEXT,                         -- JSON crudo del LLM (trazabilidad)
    tiempo_ejecucion_ms INTEGER NOT NULL,
    latencia_extraccion_ms INTEGER NOT NULL,    -- ms del paso de extracción IA
    latencia_reglas_ms INTEGER NOT NULL,        -- ms del motor de reglas
    creado_en TEXT NOT NULL                     -- ISO 8601 UTC
);

CREATE INDEX IF NOT EXISTS idx_auditorias_creado_en ON comprobante_auditoria (creado_en DESC);
