# SPEC-03: API REST y SQLite — Requisitos y Alcance

> **Audiencia:** Producto, Negocio, Revisor Técnico.
> **Estado:** Draft / Approved / In Progress / Completed

## 1. Problema de Negocio

Los módulos anteriores proveen las piezas (reglas deterministas, extracción IA), pero el evaluador necesita **un punto de entrada único y una memoria histórica**: una API HTTP que orqueste el flujo de auditoría (PDF → extracción → reglas → resultado) y un registro persistente de auditorías pasadas para trazabilidad (CU-03 del documento maestro).

Este módulo expone la API REST versionada (`/api/v1`) y la persistencia ligera en SQLite, sin servidores de bases de datos externos.

## 2. Objetivos

- [ ] Endpoint `POST /api/v1/auditar` que ejecute el flujo completo y devuelva datos + semáforo + trazabilidad en una sola respuesta.
- [ ] Endpoints de ejemplos pre-cargados (listado y servido del PDF) para demo en < 15 segundos.
- [ ] Historial de auditorías persistido en SQLite y consultable (listado paginado + detalle).
- [ ] Métrica de `tiempo_ejecucion_ms` registrada en cada auditoría, **desglosada por etapa** (`latencia_extraccion_ms` IA y `latencia_reglas_ms` motor de reglas).
- [ ] 3 PDFs de ejemplo generados por script (`backend/scripts/generar_ejemplos.py`) con fechas relativas al día de generación.

## 3. Reglas de Negocio y Restricciones

- **RN-3-01:** Solo se aceptan archivos **PDF** (`content-type` `application/pdf` o extensión `.pdf`) de hasta **5 MB** (`MAX_PDF_MB`). Exceder el tope → `413 ARCHIVO_MUY_GRANDE`; formato inválido → `422 PDF_INVALIDO`.
- **RN-3-02:** Un resultado de negocio `RECHAZADO` **no es un error HTTP**: se responde `200 OK` con `estado="RECHAZADO"` y las reglas fallidas (semáforo). Los códigos HTTP 4xx/5xx quedan reservados a fallos de infraestructura/contrato.
- **RN-3-03:** Cada auditoría genera un `id` único (`aud_` + 8 hex) y se persiste **antes de responder** (salvo fallo de extracción, que igual se registra con estado de error si resulta útil para trazabilidad — decisión: se registra con `estado="ERROR_EXTRACCION"` solo en la tabla, no en el semáforo).
- **RN-3-04:** El historial es de solo lectura vía API (no hay endpoint de borrado en el MVP).
- **RN-3-05:** SQLite corre en modo WAL con un único proceso writer; la app FastAPI usa el archivo `backend/data/sofredoc.db` configurable por `DB_PATH`.
- **RN-3-06:** La API no contiene lógica de negocio: delega en `AuditarComprobanteUseCase` (capa aplicación) y traduce errores de dominio/infraestructura a códigos HTTP.
- **RN-3-07:** Límite de **10 páginas** por comprobante (RN-2-07 de MOD-02): un PDF que las supere responde `422 PDF_INVALIDO` con mensaje específico de límite de páginas.
- **RN-3-08:** Cada auditoría persiste el desglose de latencia por etapa (extracción IA y motor de reglas) además del tiempo total.

## 4. Casos de Uso (Given-When-Then)

### CU-01: Auditoría de factura válida (flujo feliz, documento maestro)
- **Given** el operador solicita auditar el ejemplo "Factura Proveedor Homologado #001"
- **When** `POST /api/v1/auditar` recibe el PDF (vía URL de ejemplo desde el frontend)
- **Then** responde `200` con `estado="APROBADO"`, las 5 reglas en verde, los datos extraídos, `json_crudo_ia` y `tiempo_ejecucion_ms`; la auditoría queda en el historial.

### CU-02: Auditoría con inconsistencias contables o documentales
- **Given** una factura con desvío de monto o sin OC obligatoria
- **When** `POST /api/v1/auditar` procesa el documento
- **Then** responde `200` con `estado="RECHAZADO"`, indicando `codigo_error` exacto y `mensaje` legible por cada regla fallida.

### CU-03: Archivo inválido
- **Given** un archivo de 8 MB o un `.txt` renombrado
- **When** se envía a `POST /api/v1/auditar`
- **Then** responde `413` (tope) o `422` (`PDF_INVALIDO`) con cuerpo de error tipado `{ "error": {...} }`.

### CU-04: Consulta de historial
- **Given** auditorías previas persistidas
- **When** `GET /api/v1/historial?limit=20&offset=0`
- **Then** responde `200` con listado paginado ordenado por fecha descendente, sin el JSON crudo (peso); el detalle completo está en `GET /api/v1/historial/{id}`.

### CU-05: Demo con ejemplos pre-cargados
- **Given** el sistema recién instalado
- **When** `GET /api/v1/ejemplos`
- **Then** responde `200` con los 3 ejemplos (id, nombre, descripción, `resultado_esperado`, URL del PDF), y `GET /api/v1/ejemplos/{id}/pdf` entrega el PDF crudo para el visor.

## 5. Fuera de Alcance (Out of Scope)

- Autenticación/autorización (MVP sin usuarios).
- Websockets/streaming de progreso de auditoría (la UI muestra spinner simple).
- Migraciones formales (alembic): el esquema se crea con `CREATE TABLE IF NOT EXISTS` al arranque.
- Paginación por cursor, búsqueda o filtros en el historial.
- Métricas/exportación (Prometheus, CSV).
