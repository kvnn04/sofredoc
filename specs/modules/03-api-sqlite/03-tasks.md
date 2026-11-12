# TASKS-03: API REST y SQLite — Plan de Ejecución

> **Instrucción para la IA:** Ejecutar las tareas en orden estricto de dependencias. Tras completar cada tarea, marcar la casilla con `[x]` y asegurar que las pruebas unitarias sigan pasando.

## Fase 1: Persistencia (Infraestructura)

- [x] **T-01:** Definir el puerto `AuditoriaRepositoryPort` (`guardar`, `listar(limit, offset)`, `obtener(id)`) en `backend/src/domain/ports/`.
- [x] **T-02:** Crear `backend/src/infrastructure/db/esquema.sql` con el DDL de `02-design.md` §2 y aplicarlo al arranque (`CREATE TABLE IF NOT EXISTS` + índices + `PRAGMA journal_mode=WAL`).
- [x] **T-03:** Implementar `SqliteAuditoriaRepository` en `backend/src/infrastructure/db/sqlite_repository.py`: conexión configurable por `DB_PATH`, `check_same_thread=False`, serialización/deserialización JSON de columnas, mapeo fila → modelo.
- [x] **T-04:** Crear `backend/scripts/generar_ejemplos.py` (usando `reportlab`) que genera los 3 PDFs en `backend/data/ejemplos/` con fechas relativas (hoy − 5 / − 20 / − 30 días) y los datos de ejemplo definidos en la matriz de ejemplos (ver abajo); ejecutarlo y verificar los PDFs.

**Matriz de ejemplos (fuente única para script y tests):**

| id | Archivo | Caso | Datos clave | Resultado esperado |
| :--- | :--- | :--- | :--- | :--- |
| `ej-factura-aprobada` | `factura-aprobada-001.pdf` | Flujo feliz (CU-01) | CUIT `30-12345678-1` activo; ítems 2 × $175.000 = $350.000; impuestos $34.000; total $384.000; OC `OC-2026-0441`; fecha hoy−5 | `APROBADO` (5/5 verdes) |
| `ej-factura-desvio` | `factura-desvio-monto.pdf` | Desvío contable (CU-02) | CUIT `30-71234567-1` activo; ítems $200.000 + $45.000; impuestos $25.000; suma $270.000; total declarado $285.000; sin OC; fecha hoy−20 | `RECHAZADO` por R3 (`DISCREPANCIA_CONTABLE`) |
| `ej-monto-alto-sin-oc` | `factura-monto-alto-sin-oc.pdf` | Tope sin OC (CU-02) | CUIT `20-12345678-6` activo; ítem 1 × $650.000; impuestos $0; total $650.000; **sin** OC; fecha hoy−30 | `RECHAZADO` por R4 (`FALTA_ORDEN_COMPRA`) |

## Fase 2: Aplicación y Presentación

- [ ] **T-05:** Implementar `AuditarComprobanteUseCase` en `backend/src/application/auditar_comprobante.py` con inyección de puertos (pdf, extractor, padrón, clock, repositorio) siguiendo el flujo de `02-design.md` §1; medir `tiempo_ejecucion_ms` end-to-end **más el desglose por etapa** (`latencia_extraccion_ms`, `latencia_reglas_ms`) con `time.perf_counter()`; ante error de extracción, persistir `estado="ERROR_EXTRACCION"` y propagar el error tipado.
- [ ] **T-06:** Definir DTOs de `backend/src/presentation/dtos.py` (incluye serialización de montos con 2 decimales).
- [ ] **T-07:** Exponer `POST /api/v1/auditar` en `backend/src/presentation/routers/auditar.py`: validaciones de tamaño (`413`) y MIME/parseo (`422`) antes del caso de uso; respuesta `200` con `ResultadoAuditoriaDTO` (RN-3-02).
- [ ] **T-08:** Exponer `GET /api/v1/ejemplos` y `GET /api/v1/ejemplos/{id}/pdf` en `backend/src/presentation/routers/ejemplos.py` (catálogo estático leído de `data/ejemplos/`; `StreamingResponse` para el PDF).
- [ ] **T-09:** Exponer `GET /api/v1/historial` (limit/offset, default 20/0, orden `creado_en DESC`, sin `json_crudo_ia`) y `GET /api/v1/historial/{id}` (completo) en `backend/src/presentation/routers/historial.py`.
- [ ] **T-10:** Implementar `backend/src/presentation/errores.py`: mapeo de excepciones de dominio/infra (`PDF_INVALIDO`, `PDF_SIN_TEXTO`, `PdfDemasiadasPaginasError` → `PDF_INVALIDO` con mensaje de límite de páginas, `EXTRACCION_FALLIDA`, etc.) a `HTTPException` con el cuerpo de error tipado §3; registrar los handlers en la app.

## Fase 3: Integración y Tests

- [ ] **T-11:** Wire-up en `main.py`: routers + creación de tablas al arranque + inyección de dependencias (factory del extractor según `EXTRACTOR_MODE`).
- [ ] **T-12:** Tests de integración `backend/tests/integration/test_api_auditar.py` (TestClient + SQLite temporal + extractor mock): CU-01 APROBADO, CU-02 RECHAZADO con `DISCREPANCIA_CONTABLE` y `FALTA_ORDEN_COMPRA`, CU-03 `413`/`422`, verificación de fila persistida en SQLite.
- [ ] **T-13:** Tests de integración `backend/tests/integration/test_api_historial.py`: listado paginado, detalle, `404`, y `GET /api/v1/ejemplos` + `/ejemplos/{id}/pdf` (content-type y tamaño > 0).
