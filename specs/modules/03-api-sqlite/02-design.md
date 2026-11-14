# DESIGN-03: API REST y SQLite — Diseño Técnico

> **Audiencia:** Ingenieros de Software, Agentes de IA.
> **Patrón:** Clean Architecture (Monolito FastAPI + React).

## 1. Arquitectura de Componentes y Capas

```text
backend/src/
├── application/
│   └── auditar_comprobante.py     # AuditarComprobanteUseCase (orquestador)
├── infrastructure/db/
│   ├── sqlite_repository.py       # AuditoriaRepository (implementa el puerto)
│   └── esquema.sql                # DDL (creado en arranque)
└── presentation/
    ├── dtos.py                    # Request/Response models (API-facing)
    ├── errores.py                 # Mapeo excepción → HTTPException
    └── routers/
        ├── auditar.py             # POST /api/v1/auditar
        ├── ejemplos.py            # GET /api/v1/ejemplos, GET /api/v1/ejemplos/{id}/pdf
        └── historial.py           # GET /api/v1/historial, GET /api/v1/historial/{id}
```

### Flujo del caso de uso (application)

```text
AuditarComprobanteUseCase.ejecutar(pdf: bytes, nombre_archivo: str)
 1. pdf_port.extraer_texto(pdf)                        # infrastructure/pdf (MOD-02)
 2. extractor.extraer(texto, nombre_archivo)           # mock|llm (MOD-02) → ExtraccionResultado
 3. padrón.buscar(CUIT) + clock.hoy()                  # contexto para reglas (MOD-01)
 4. engine.evaluar(factura, contexto)                  # 5 reglas (MOD-01) → ResultadoAuditoria
 5. repo.guardar(auditoria)                            # SQLite (incluye latencias por etapa)
 6. → ResultadoAuditoriaDTO (id, estado, datos, reglas, json_crudo,
     tiempo_ejecucion_ms + latencia_extraccion_ms + latencia_reglas_ms)
```

> El use case cronometra cada etapa con `time.perf_counter()` y redondea a ms enteros.

## 2. Modelos de Datos y Esferas de Dominio

### Esquema de Base de Datos (SQLite)

```sql
-- backend/src/infrastructure/db/esquema.sql
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
```

- Conexión: `sqlite3.connect(db_path, check_same_thread=False)` + `PRAGMA journal_mode=WAL` al inicializar.
- El repositorio implementa el puerto de dominio `AuditoriaRepositoryPort` (`guardar`, `listar(limit, offset)`, `obtener(id)`).

### DTOs de presentación (request/response)

```python
# backend/src/presentation/dtos.py (esencia)
class ReglaResultadoDTO(BaseModel):
    codigo: str
    nombre: str
    aprobado: bool
    mensaje: str
    codigo_error: str | None = None

class ResultadoAuditoriaDTO(BaseModel):
    id: str
    estado: Literal["APROBADO", "RECHAZADO", "ERROR_EXTRACCION"]
    nombre_archivo: str
    datos_extraidos: dict | None
    reglas_evaluadas: list[ReglaResultadoDTO]
    json_crudo_ia: dict | None
    tiempo_ejecucion_ms: int
    latencia_extraccion_ms: int
    latencia_reglas_ms: int
    creado_en: str
```

> Los montos `Decimal` del dominio se serializan a JSON como número con 2 decimales (convención global de `specs/README.md`); en SQLite se guardan como REAL y el JSON de `datos_extraidos` lleva el valor numérico.

## 3. Contratos de API (HTTP / JSON)

### Endpoints

| Método | Ruta | Descripción | Errores |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/auditar` | multipart `file` (PDF ≤ 5 MB) → auditoría completa | 413, 422, 502 |
| `GET` | `/api/v1/ejemplos` | Lista de los 3 ejemplos pre-cargados | — |
| `GET` | `/api/v1/ejemplos/{id}/pdf` | PDF crudo del ejemplo (`application/pdf`) | 404 |
| `GET` | `/api/v1/historial?limit=20&offset=0` | Listado paginado (sin JSON crudo) | — |
| `GET` | `/api/v1/historial/{id}` | Detalle completo de una auditoría | 404 |
| `GET` | `/api/v1/health` | Salud del servicio (MOD-00) | — |

### Endpoint: `POST /api/v1/auditar`
- **Request (multipart/form-data):** `file`: Archivo PDF (máx. 5 MB).
- **Response `200 OK` (ejemplo CU-01):**
```json
{
  "id": "aud_9f2c1a7b",
  "estado": "APROBADO",
  "nombre_archivo": "factura-aprobada-001.pdf",
  "datos_extraidos": {
    "tipo_comprobante": "FACTURA",
    "letra_comprobante": "A",
    "numero_comprobante": "00001-00000123",
    "cuit_emisor": "30-12345678-1",
    "razon_social": "Distribuidora Andina S.A.",
    "fecha_emision": "2026-11-07",
    "numero_orden_compra": "OC-2026-0441",
    "items": [
      { "descripcion": "Servicio de instalación torre 4G", "cantidad": 2, "precio_unitario": 175000.00, "subtotal": 350000.00 }
    ],
    "detalle_impuestos": [
      { "concepto": "Impuestos", "monto": 34000.00 }
    ],
    "impuestos": 34000.00,
    "monto_total": 384000.00
  },
  "reglas_evaluadas": [
    { "codigo": "R1", "nombre": "Integridad de CUIT",       "aprobado": true, "mensaje": "CUIT válido (dígito verificador correcto).", "codigo_error": null },
    { "codigo": "R2", "nombre": "Proveedor Habilitado",     "aprobado": true, "mensaje": "Proveedor activo en el padrón.", "codigo_error": null },
    { "codigo": "R3", "nombre": "Consistencia Matemática",  "aprobado": true, "mensaje": "Suma de ítems + impuestos coincide con el total.", "codigo_error": null },
    { "codigo": "R4", "nombre": "Tope sin Orden de Compra", "aprobado": true, "mensaje": "OC presente.", "codigo_error": null },
    { "codigo": "R5", "nombre": "Vigencia del Comprobante", "aprobado": true, "mensaje": "Fecha de emisión dentro de la vigencia (60 días).", "codigo_error": null }
  ],
  "json_crudo_ia": { "tipo_comprobante": "FACTURA", "cuit_emisor": "30-12345678-1" },
  "tiempo_ejecucion_ms": 1420,
  "latencia_extraccion_ms": 1287,
  "latencia_reglas_ms": 3,
  "creado_en": "2026-11-12T18:04:05Z"
}
```
- **Fragmento `reglas_evaluadas` en un caso `RECHAZADO` (CU-02):**
```json
[
  { "codigo": "R3", "nombre": "Consistencia Matemática", "aprobado": false,
    "mensaje": "La suma de ítems + impuestos ($270.000,00) no coincide con el total declarado ($285.000,00).",
    "codigo_error": "DISCREPANCIA_CONTABLE",
    "detalles": { "calculado": 270000.00, "declarado": 285000.00 } },
  { "codigo": "R4", "nombre": "Tope sin Orden de Compra", "aprobado": false,
    "mensaje": "Comprobante de $725.000 supera el tope de $500.000 sin Orden de Compra.",
    "codigo_error": "FALTA_ORDEN_COMPRA" }
]
```

### Errores tipados

```json
{ "error": { "codigo": "ARCHIVO_MUY_GRANDE", "mensaje": "El archivo supera el tope de 5 MB." } }
```

| Código | HTTP | Causa |
| :--- | :---: | :--- |
| `ARCHIVO_MUY_GRANDE` | 413 | PDF > `MAX_PDF_MB` |
| `PDF_INVALIDO` | 422 | No es PDF / no parseable / más de 10 páginas |
| `PDF_SIN_TEXTO` | 422 | PDF escaneado sin capa de texto |
| `EXTRACCION_FALLIDA` | 502 | El LLM no produjo un esquema válido tras reintento |
| `AUDITORIA_NO_ENCONTRADA` | 404 | id inexistente en historial |
| `EJEMPLO_NO_ENCONTRADO` | 404 | id de ejemplo inexistente |

## 4. Librerías y Dependencias Elegidas

- `fastapi` + `python-multipart` (upload), `sqlite3` stdlib (sin ORM), `pytest` + `httpx` (`TestClient`) para integración.
- Los 3 PDFs de ejemplo se generan con `reportlab` (única dependencia del script `generar_ejemplos.py`) y fechas relativas: hoy − 5 días, hoy − 20 días, hoy − 30 días.
