# VERIFICATION-05: QA: Pytest, Playwright & k6 — Testing y Cierre

> **Audiencia:** QA, Lead Developer, CI/CD.

## 1. Pruebas Unitarias e Integración (Pytest)

```bash
# Correr pruebas de dominio y reglas
pytest backend/tests/unit -v

# Correr pruebas integradas de API y base de datos
pytest backend/tests/integration -v

# Suite completo + gate de cobertura
pytest backend/tests -v --cov=src --cov-report=term-missing --cov-fail-under=95
```

### Cobertura Mínima Requerida
- Domain / Rules Engine: **100%**
- Application / Use Cases: **> 90%**
- Infrastructure (db, pdf, llm adapters): > 90%
- Tiempo del suite completo: < 30 s (sin red).

## 2. Pruebas E2E (Playwright)

```bash
npx playwright test qa/e2e/auditoria.spec.ts
```

- [x] Verificar la carga de los 3 ejemplos pre-cargados (resultados: APROBADO / RECHAZADO-R3 / RECHAZADO-R4).
- [x] Confirmar actualización visual del semáforo (`APROBADO` vs `RECHAZADO`).
- [x] Validar visualización del panel de JSON Pydantic (plegado → desplegado → copiable, Pydantic + crudo IA).
- [x] Verificar el desglose de latencia por etapa (IA / reglas / total) junto al badge de estado.
- [x] Historial: ≥ 3 filas tras los 3 escenarios, con latencia en ms y recarga de detalle.
- [x] Subida propia (CU-05, RN-4-03/RN-4-04): `.txt` → banner `PDF_INVALIDO`, 6 MB → `ARCHIVO_MUY_GRANDE`, ambos sin perder el empty-state; PDF real → `APROBADO` con el visor apuntando a `iframe[src^="blob:"]` y estado "Auditando…" (botón deshabilitado + skeleton) asertado amplificando la latencia del POST con `page.route` (ADR-05-07).
- [x] Dos pasadas consecutivas en verde (cero flakes, `retries: 0`). *(4 escenarios: 3 pasadas 24,3 / 18,7 / 19,4 s. Con el escenario 5 de subida propia: 2 pasadas más, 33,5 s / 31,3 s — 5/5 passed cada una. Con la extensión ADR-05-08: 10/10 passed en 2 pasadas consecutivas (1.3 m / 34,4 s).)*
- [x] Extensión de cobertura E2E (ADR-05-08): REMITO → admisión R0 con 1 sola regla evaluada (`REMITO_NO_AUDITABLE` sin cortocircuito); PDF sin capa de texto → `PDF_SIN_TEXTO` del backend real sin consumir IA; PDF de 11 páginas → `PDF_INVALIDO` (tope 10 páginas server-side); red caída → banner `ERROR_RED` con el resultado previo conservado (CU-05); `EXTRACCION_FALLIDA` (502 simulado con `page.route`) → banner tipado y resultado previo intacto (CU-05). *(10/10 passed × 2 pasadas; PDFs fixture commiteados en `qa/e2e/fixtures/`, generados por `backend/scripts/generar_fixtures_e2e.py`.)*

## 3. Pruebas de Estrés y Rendimiento (k6)

Ejecutar k6 en modo `EXTRACTOR_MODE=mock` para evaluar concurrencia y la base SQLite sin consumir créditos de IA:

```bash
EXTRACTOR_MODE=mock uvicorn src.main:app --port 8000 &
k6 run qa/load/stress_test.js
```

### Umbrales (SLOs / SLAs)

Corrida completa (T-09, 2026-11-12): backend uvicorn `EXTRACTOR_MODE=mock` en `:8000` con
`DB_PATH=qa/artifacts/k6-sofredoc.db` (efímera, RN-5-05). Escenario: rampa 30 s a 50 VUs,
meseta 60 s, drenaje 15 s (105 s totales). Throughput: **164,95 req/s** (17.322 requests,
5.774 iteraciones a 54,98/s), 23.096/23.096 checks OK.

| Métrica | Umbral | Resultado obtenido | ✅/❌ |
| :--- | :--- | :--- | :---: |
| Tasa de error (`http_req_failed`) | < 1% | **0.00%** (0 de 17.322 requests) | ✅ |
| Latencia p95 (`http_req_duration`) | < 500 ms | **449.35 ms** (p50 = 239.08 ms) | ✅ |
| Concurrencia objetivo | 50 VUs | 50 VUs en meseta (60 s) | ✅ |

Smoke para CI (T-10, `SMOKE=1`): 10 VUs × 30 s → p95 **71.93 ms**, tasa de error **0.00%**,
1.521 iteraciones (50,5/s), 6.084/6.084 checks OK.

Observación: a 50 VUs el p95 (449 ms) queda cerca del umbral: el cuello de botella es la
conexión SQLite compartida con lock (el repositorio serializa inserts y lecturas), no la
extracción mock (< 10 ms). Para la PoC es aceptable; escalar a Postgres/pool de conexiones
está fuera de alcance (nota de DESIGN-05 §5).

## 4. Registro de Decisiones de Arquitectura (ADR Log)

> **Índice maestro:** todas las decisiones del proyecto —numeradas y de base— están catalogadas en el índice [`adr/README.md`](../../adr/README.md). El texto completo vive en [`specs/adr/`](../../adr/): los 10 ADRs numerados como archivos individuales y las decisiones de base en [`base-02-05-extraccion-api-ui-qa.md`](../../adr/base-02-05-extraccion-api-ui-qa.md). Esta sección queda como tabla resumen de navegación.

### Decisiones de base (sin ID)

Texto completo (motivo e impacto): [`base-02-05-extraccion-api-ui-qa.md` · MOD-05](../../adr/base-02-05-extraccion-api-ui-qa.md#mod-05-qa-playwright-y-k6)

| Fecha | Decisión |
| :--- | :--- |
| 2026-11-12 | Uso de `EXTRACTOR_MODE=mock` |
| 2026-11-12 | `retries: 0` en Playwright |
| 2026-11-12 | Clock fijo `2026-11-12` en fixtures unitarios |
| 2026-11-12 | Gate de cobertura como parte del DoD |
| 2026-11-12 | k6 smoke de 10 VUs para CI |
| 2026-11-12 | Deploy de cierre en Render + Vercel |

### Decisiones formales (numeradas)

| ID | Fecha | Decisión | Archivo |
| :--- | :--- | :--- | :--- |
| ADR-05-01 | 2026-11-12 | Mock resuelve fixture por identidad del ejemplo | [→](../../adr/adr-05-01-mock-por-identidad-del-ejemplo.md) |
| ADR-05-02 | 2026-11-12 | Reset de BD efímera dentro del comando del webServer | [→](../../adr/adr-05-02-reset-bd-en-webserver.md) |
| ADR-05-03 | 2026-11-12 | El E2E no aserta el render interno del visor | [→](../../adr/adr-05-03-e2e-no-aserta-visor.md) |
| ADR-05-04 | 2026-11-12 | k6 corre contra BD efímera en artifacts | [→](../../adr/adr-05-04-k6-contra-bd-efimera.md) |
| ADR-05-05 | 2026-11-12 | Workflow único de verificación sin deploy automático | [→](../../adr/adr-05-05-workflow-ci-sin-deploy.md) |
| ADR-05-06 | 2026-11-12 | Cuello de botella en el lock de SQLite a 50 VUs | [→](../../adr/adr-05-06-cuello-de-botella-lock-sqlite.md) |
| ADR-05-07 | 2026-11-12 | Estado de carga asertado con page route | [→](../../adr/adr-05-07-estado-de-carga-con-page-route.md) |
| ADR-05-08 | 2026-11-13 | E2E extendido a 10 escenarios con fixture REMITO | [→](../../adr/adr-05-08-e2e-10-escenarios-y-remito.md) |
| ADR-05-09 | 2026-11-13 | Puertos exclusivos del E2E 8010 y 5175 | [→](../../adr/adr-05-09-puertos-exclusivos-e2e.md) |
| ADR-05-10 | 2026-11-13 | k6 funcional separado del de saturación | [→](../../adr/adr-05-10-k6-funcional-separado.md) |

## 5. Criterio de Aceptación Final (Definition of Done) — Proyecto Completo

- [x] Todas las tareas de `03-tasks.md` de **los 6 módulos** están marcadas como `[x]`. *(Cerrado 2026-11-15: T-14..T-16 ejecutadas por Kevin — deploy Render + Vercel con smoke en verde; barrido de los 6 `03-tasks.md` confirmó cero checkboxes pendientes.)*
- [x] Todos los tests de Pytest pasan en verde (`unit` + `integration`, < 30 s, sin red). *(DoD 2026-11-15: **129 passed en 7.31 s**.)*
- [x] Cobertura: dominio 100%, aplicación > 90% (gate activo). *(DoD 2026-11-15: dominio 100%, aplicación 100%, total **99.61%** con `--cov-fail-under=95`.)*
- [x] Los tests de Playwright se ejecutan correctamente sin flakiness (2 pasadas). *(DoD 2026-11-15: **10/10 passed × 2 pasadas consecutivas (1.4 m / 35.7 s)**, `retries: 0`, EXIT=0.)*
- [x] k6 cumple con los SLAs de latencia (p95 < 500 ms) y tasa de error (< 1%) con 50 VUs en modo mock. *(DoD 2026-11-15: **0.00% errores (0/16.872), p95 462.69 ms**, 22.496/22.496 checks, EXIT=0, BD efímera propia `k6-dod-20261115.db`; corrida original 2026-11-12: p95 449.35 ms — §3.)*
- [x] Los 3 PDFs de ejemplo son válidos y vigentes (fechas dentro de los 60 días de R5). *(DoD 2026-11-15: vigentes — vencimiento por R5: ejemplo R4 (`extraccion-monto-alto-sin-oc.json`, fecha 2026-10-13) → **2026-12-12**; aprobada/desvío (2026-11-07) → 2027-01-06. Regenerar `scripts/generar_ejemplos.py` + refrescar fixtures antes de esas fechas.)*
- [x] La demo completa corre de cero con 2 comandos (backend + frontend) en < 15 s de setup post-instalación. *(Quickstart del README raíz.)*
- [x] `specs/README.md` refleja el estado real (🟢 Completado) y cada `04-verification.md` tiene su ADR log completo. *(2026-11-15: MOD-05 → 🟢 tras el deploy; los 6 módulos 🟢 y los ADR logs completos — ADR-02-01..12, ADR-03-01..08, ADR-04-01..07, ADR-05-01..10.)*
- [x] Backend y frontend desplegados (Render + Vercel) con smoke post-deploy en verde y URLs documentadas. *(Hecho 2026-11-15: https://sofredoc-api.onrender.com (Render) + https://sofredoc.vercel.app (Vercel); smoke por Kevin en vivo — health 200, matriz de verdad completa, semáforo, JSON inspector e historial; ambos modos (`mock`/`llm`) verificados, queda `mock`. URLs y notas operativas en README raíz §"Producción"; guía en `docs/despliegue.md`.)*
- [x] `README.md` raíz con quickstart, arquitectura, sección de calidad y capturas de la demo. *(Capturas reales del E2E en `docs/capturas/`.)*
