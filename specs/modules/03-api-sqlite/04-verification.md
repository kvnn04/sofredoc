# VERIFICATION-03: API REST y SQLite — Testing y Cierre

> **Audiencia:** QA, Lead Developer, CI/CD.

## 1. Pruebas Unitarias e Integración (Pytest)

```bash
# Correr pruebas integradas de API y base de datos
pytest backend/tests/integration -v

# Suite completo del backend (unit + integration)
pytest backend/tests -v --cov=src --cov-report=term-missing
```

### Cobertura Mínima Requerida
- Application / Use Cases (`AuditarComprobanteUseCase`): **> 90%**
- Infrastructure/db (repositorio SQLite): **> 90%**
- Presentation/routers: cubiertos por los tests de integración (flujos felices + errores tipados).

### Matriz de Verificación de Integración

| # | Escenario | Request | Esperado |
| :--- | :--- | :--- | :--- |
| 1 | Flujo feliz (ejemplo aprobado) | POST con `ej-factura-aprobada` (bytes) | 200, `estado=APROBADO`, 5 reglas `aprobado=true`, `id` con formato `aud_*`, fila persistida |
| 2 | Desvío contable | POST con `ej-factura-desvio` | 200, `estado=RECHAZADO`, R3 con `DISCREPANCIA_CONTABLE` y mensaje con montos |
| 3 | Tope sin OC | POST con `ej-monto-alto-sin-oc` | 200, `estado=RECHAZADO`, R4 con `FALTA_ORDEN_COMPRA` |
| 4 | Archivo > 5 MB | POST con blob de 6 MB | 413 `ARCHIVO_MUY_GRANDE` |
| 5 | No-PDF | POST con `archivo.txt` | 422 `PDF_INVALIDO` |
| 6 | PDF sin texto | POST con PDF de imagen | 422 `PDF_SIN_TEXTO` |
| 7 | Extracción fallida | extractor stub que siempre falla | 502 `EXTRACCION_FALLIDA` |
| 8 | Historial paginado | GET `/historial?limit=2&offset=0` tras 3 auditorías | 200, 2 ítems, orden descendente por `creado_en` |
| 9 | Detalle | GET `/historial/{id}` | 200 con `json_crudo_ia`; GET id inexistente → 404 `AUDITORIA_NO_ENCONTRADA` |
| 10 | Ejemplos | GET `/ejemplos` + `/ejemplos/{id}/pdf` | 200 con 3 ítems y PDF `application/pdf` > 0 bytes |
| 11 | Multi-página | POST con PDF de 11 páginas (fixture) | 422 `PDF_INVALIDO` con mensaje de límite de páginas |

## 2. Pruebas E2E (Playwright)

Cubiertas en MOD-05 sobre esta API ya desplegada localmente.

## 3. Pruebas de Estrés y Rendimiento (k6)

Cubiertas en MOD-05 (con `EXTRACTOR_MODE=mock` esta API sostiene 50 VUs con p95 < 500 ms objetivo).

## 4. Registro de Decisiones de Arquitectura (ADR Log)

> **Índice maestro:** todas las decisiones del proyecto —numeradas y de base— están catalogadas en el índice [`adr/README.md`](../../adr/README.md). El texto completo vive en [`specs/adr/`](../../adr/): los 8 ADRs numerados como archivos individuales y las decisiones de base en [`base-02-05-extraccion-api-ui-qa.md`](../../adr/base-02-05-extraccion-api-ui-qa.md). Esta sección queda como tabla resumen de navegación.

### Decisiones de base (sin ID)

Texto completo (motivo e impacto): [`base-02-05-extraccion-api-ui-qa.md` · MOD-03](../../adr/base-02-05-extraccion-api-ui-qa.md#mod-03-api-rest-y-sqlite)

| Fecha | Decisión |
| :--- | :--- |
| 2026-11-12 | `RECHAZADO` responde `200 OK` |
| 2026-11-12 | Estado `ERROR_EXTRACCION` solo en tabla |
| 2026-11-12 | SQLite WAL + `check_same_thread=False` |
| 2026-11-12 | PDFs de ejemplo generados por script con fechas relativas |
| 2026-11-12 | Montos `Decimal` → REAL + JSON numérico 2 decimales |
| 2026-11-12 | Latencia desglosada por etapa (IA / reglas) |
| 2026-11-12 | SQLite efímero en deploy (free tier) |

### Decisiones formales (numeradas)

| ID | Fecha | Decisión | Archivo |
| :--- | :--- | :--- | :--- |
| ADR-03-01 | 2026-11-12 | DTOs con cuit_emisor y monto_total planos | [→](../../adr/adr-03-01-dtos-con-cuit-y-monto-planos.md) |
| ADR-03-02 | 2026-11-12 | App construida perezosamente con __getattr__ | [→](../../adr/adr-03-02-app-perezosa-con-getattr.md) |
| ADR-03-03 | 2026-11-12 | Conexión SQLite con threading.Lock y cierre en lifespan | [→](../../adr/adr-03-03-sqlite-con-lock-y-cierre.md) |
| ADR-03-04 | 2026-11-12 | Errores vía handlers de excepción | [→](../../adr/adr-03-04-errores-via-handlers.md) |
| ADR-03-05 | 2026-11-12 | Escenario R4 probado con extractor stub | [→](../../adr/adr-03-05-escenario-r4-extractor-stub.md) |
| ADR-03-06 | 2026-11-12 | reportlab solo para el script de ejemplos | [→](../../adr/adr-03-06-reportlab-solo-para-ejemplos.md) |
| ADR-03-07 | 2026-11-12 | Montos de datos_extraidos como número JSON | [→](../../adr/adr-03-07-montos-como-numero-json.md) |
| ADR-03-08 | 2026-11-13 | Desempate del historial por rowid DESC | [→](../../adr/adr-03-08-desempate-historial-por-rowid.md) |

## 5. Criterio de Aceptación Final (Definition of Done)

- [x] Todas las tareas de `03-tasks.md` están marcadas como `[x]`.
- [x] Todos los tests de integración pasan en verde contra SQLite temporal (sin tocar `data/sofredoc.db` real).
- [x] Los 10 escenarios de la matriz §1 verificados (11 filas: 1–7 y 11 en `test_api_auditar.py`; 8–10 en `test_api_historial.py`).
- [x] Los 3 PDFs de ejemplo existen y los endpoints `/ejemplos` y `/ejemplos/{id}/pdf` los sirven.
- [x] `curl` manual de la matriz de contratos reproduce las respuestas de `02-design.md` §3 (uvicorn real: `/health`, `/ejemplos`, `/ejemplos/{id}/pdf`, `POST /auditar` 200/413/422, `/historial` paginado sin `json_crudo_ia`, `/historial/{id}` con JSON crudo, 404 tipados).
- [x] Un flujo completo manual (mock mode) audita un PDF en < 2 s end-to-end (34 ms medidos).
