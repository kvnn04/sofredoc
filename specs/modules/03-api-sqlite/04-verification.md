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

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | `RECHAZADO` responde `200 OK` | El rechazo es un **resultado de negocio** válido; 4xx/5xx reservados a fallos de contrato/infra. | La UI distingue estado del semáforo, no códigos HTTP, para el semáforo. |
| 2026-11-12 | Estado `ERROR_EXTRACCION` solo en tabla | Trazabilidad de fallos sin contaminar el semáforo de reglas. | `reglas_evaluadas=[]` en ese estado. |
| 2026-11-12 | SQLite WAL + `check_same_thread=False` | PoC mono-proceso con concurrencia moderada (k6 50 VUs de solo lectura + escrituras acotadas). | Tope práctico de escrituras concurrentes; suficiente para MVP. |
| 2026-11-12 | PDFs de ejemplo generados por script con fechas relativas | Los ejemplos deben permanecer vigentes (R5: 60 días) sin regeneración manual periódica. | Re-ejecutar `generar_ejemplos.py` si la demo envejece > 60 días. |
| 2026-11-12 | Montos `Decimal` → REAL + JSON numérico 2 decimales | Precisión en dominio; legibilidad en UI. | Conversión explícita en DTOs. |
| 2026-11-12 | Latencia desglosada por etapa (IA / reglas) | Confirmado por el product owner: hace visible la arquitectura híbrida ante el evaluador técnico. | 2 columnas nuevas en SQLite + campos en DTO y UI. |
| 2026-11-12 | SQLite efímero en deploy (free tier) | Render reinicia el disco en cada deploy; el historial es volátil en producción gratuita. | Nota obligatoria en README y smoke post-deploy (MOD-05 §5). |
| 2026-11-12 | ADR-03-01: DTOs con `cuit_emisor` y `monto_total` planos | El diseño §2 (esencia) solo los lleva dentro de `datos_extraidos`; el listado del historial los necesita accesibles sin traer `datos_extraidos` completo (y en `ERROR_EXTRACCION` esos datos son NULL). | Campos adicionales (aditivos, no rompen el contrato §3). |
| 2026-11-12 | ADR-03-02: `app` de `main.py` se construye perezosamente (`__getattr__`) | Importar `src.main` desde los tests no debe crear `data/sofredoc.db` real; `uvicorn src.main:app` sigue funcionando (verificado en el smoke manual). | DoD §5 b-2: los tests no tocan la BD real (smoke usa settings temporales). |
| 2026-11-12 | ADR-03-03: conexión SQLite con `threading.Lock` + `cerrar()` en lifespan | Los endpoints sync corren en el threadpool de FastAPI; el lock serializa el acceso a la conexión compartida y el cierre evita `ResourceWarning`. | Sin cambios de contrato; robustez bajo concurrencia. |
| 2026-11-12 | ADR-03-04: errores de presentación vía handlers de excepción (no `HTTPException`) | El contrato §3 exige cuerpo `{"error": {...}}` sin el wrapper `detail` de FastAPI; los routers levantan `ErrorHTTPTipado` y el dominio `ErrorTipificado` se mapea por `codigo`. | Cuerpos de error idénticos a §3 en todos los endpoints. |
| 2026-11-12 | ADR-03-05: escenario R4 (`FALTA_ORDEN_COMPRA`) se prueba con extractor stub | El mock solo trae variantes `aprobada`/`rechazado` (R3); la fila 3 de la matriz se verifica inyectando un extractor fijo en `create_app`. El flujo end-to-end real con LLM queda en la verificación pendiente de MOD-02 §2. | Sin cambios en `MOCK_VARIANT` ni en contratos. |
| 2026-11-12 | ADR-03-06: `reportlab` en requirements.txt | Declarada por DESIGN-03 §4 como dependencia única del script `generar_ejemplos.py`; no se usa en `src/` (el dominio y los tests generan PDFs mínimos sin ella). | requirements.txt: `reportlab>=4.0`. |
| 2026-11-12 | ADR-03-07: montos de `datos_extraidos` como número (no string) | pydantic v2 serializa `Decimal` como string en modo JSON; la convención global exige número con 2 decimales → conversor explícito en el caso de uso. | `monto_total: 384000.0` (número) en JSON, como en el ejemplo §3. |
| 2026-11-13 | **ADR-03-08:** desempate del listado del historial por `rowid DESC` (`ORDER BY creado_en DESC, rowid DESC`) | Bug de CI detectado en el E2E escenario 4: `creado_en` tiene precisión de segundos y en el runner (rápido, ~1,3 s/test) las auditorías del escenario 2 y 3 cayeron en el mismo segundo → el `ORDER BY creado_en DESC` sin desempate devolvía empates en orden indefinido y la UI cargó como "más reciente" la auditoría del escenario 2 (R3) en vez de la del escenario 3 (R4). El contrato CU-04 ("el más nuevo primero") se mantiene: con empate de segundo, el más nuevo es el último insertado (`rowid` refleja el orden de inserción). Sin cambios de DDL, contrato API ni reglas. | pytest **111 passed** (+1 test de integración que reproduce el empate: 3 filas mismo segundo → orden de inserción invertido, determinístico); cobertura total 99.59% (gate ≥95%). E2E re-verificado en verde tras el fix. |

## 5. Criterio de Aceptación Final (Definition of Done)

- [x] Todas las tareas de `03-tasks.md` están marcadas como `[x]`.
- [x] Todos los tests de integración pasan en verde contra SQLite temporal (sin tocar `data/sofredoc.db` real).
- [x] Los 10 escenarios de la matriz §1 verificados (11 filas: 1–7 y 11 en `test_api_auditar.py`; 8–10 en `test_api_historial.py`).
- [x] Los 3 PDFs de ejemplo existen y los endpoints `/ejemplos` y `/ejemplos/{id}/pdf` los sirven.
- [x] `curl` manual de la matriz de contratos reproduce las respuestas de `02-design.md` §3 (uvicorn real: `/health`, `/ejemplos`, `/ejemplos/{id}/pdf`, `POST /auditar` 200/413/422, `/historial` paginado sin `json_crudo_ia`, `/historial/{id}` con JSON crudo, 404 tipados).
- [x] Un flujo completo manual (mock mode) audita un PDF en < 2 s end-to-end (34 ms medidos).
