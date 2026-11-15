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

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | Uso de `EXTRACTOR_MODE=mock` | Evitar llamadas al LLM durante pruebas k6. | Pruebas de estrés deterministas y sin costo. |
| 2026-11-12 | `retries: 0` en Playwright | Los reintentos ocultan flakes (RN-5-06); el reporte debe reflejar la realidad. | Un flake detiene el cierre y se investiga. |
| 2026-11-12 | Clock fijo `2026-11-12` en fixtures unitarios | R5 depende de "hoy"; fecha fija hace los tests reproducibles para siempre. | Regenerar solo si cambia el algoritmo (requiere ADR). |
| 2026-11-12 | Gate de cobertura como parte del DoD | El motor de reglas audita decisiones contables; sin 100% de dominio no hay garantía. | `--cov-fail-under` en el comando oficial. |
| 2026-11-12 | k6 smoke de 10 VUs para CI | Meseta de 50 VUs es lenta para pipeline; el smoke valida regeneración sin exceder tiempos. | Opcional, señal temprana de regresiones. |
| 2026-11-12 | Deploy de cierre en Render + Vercel | Confirmado por el product owner: el MVP debe poder evaluarse sin instalar nada. | SQLite efímero en free tier → historial volátil, documentado. |
| 2026-11-12 | **ADR-05-01:** el mock resuelve la fixture por identidad del ejemplo (nombre de archivo `ej-…` o el PDF original re-subido) | Los E2E (RN-5-04) corren en modo mock sin `LLM_API_KEY`: sin esto los 3 ejemplos darían APROBADO y los escenarios R3/R4 serían imposibles. No cambia contrato API, esquema de BD ni reglas de negocio. | Matriz de verdad reproducible en demo y E2E (T-06); fixture nueva `extraccion-monto-alto-sin-oc.json` con fecha estática 2026-10-13 (mismo riesgo de vencimiento que ADR-02-06: regenerar si la demo envejece). |
| 2026-11-12 | **ADR-05-02:** reset de la BD efímera dentro del comando del `webServer` (`qa/e2e/reset-db.mjs`) | Playwright arranca los `webServer` **antes** del `globalSetup`: borrar la BD ahí fallaba con EPERM (archivo abierto por uvicorn). | Cada corrida E2E empieza de cero (reproducible); RN-5-05 intacta. |
| 2026-11-12 | **ADR-05-03:** el E2E no aserta sobre el visor de PDF | Chromium headless no renderiza PDFs en línea (iframe vacío); el flujo auditado es completo. | Limitación del navegador headless, no del producto; en navegador real el visor muestra el PDF. |
| 2026-11-12 | **ADR-05-04:** k6 corre contra BD efímera `qa/artifacts/k6-sofredoc.db` | RN-5-05: ningún test de carga toca `backend/data/sofredoc.db`. | Medición sobre SQLite en disco, igual que la corrida local. |
| 2026-11-12 | **ADR-05-05:** workflow único de verificación, sin deploy automático | SPEC-05 §5: el deploy de cierre es manual/scriptado; CI valida calidad en cada push. | Orden `pytest → ruff → build → playwright → k6 smoke` con reportes como artefactos. |
| 2026-11-12 | **ADR-05-06 (observación):** p95 de 449 ms a 50 VUs, cerca del umbral | Cuello de botella: la conexión SQLite compartida con lock serializa inserts y lecturas (la extracción mock tarda < 10 ms). | Aceptable para la PoC; escalar a Postgres/pool de conexiones queda fuera de alcance (nota de DESIGN-05 §5). |
| 2026-11-12 | **ADR-05-07:** el estado "Auditando…" del escenario 5 se aserta amplificando la latencia del `POST /auditar` con `page.route` (delay 800 ms); backend real intacto. | La auditoría mock responde en < 10 ms: el estado de carga es demasiado breve para asertarlo de forma estable sin `retries` (RN-5-06). El delay se agrega solo en el navegador del test. | El E2E verifica spinner + botón deshabilitado + skeleton sin flake; también aserta que el visor recibe `iframe[src^="blob:"]` (RN-4-04) sin afirmar el render interno del PDF (ADR-05-03 se mantiene). |
| 2026-11-13 | **ADR-05-08:** extensión del E2E a 10 escenarios + fixture REMITO en el MockExtractor | Kevin pidió ≥ 5 casos nuevos. Se agregan: (a) marca `"remito"` en el nombre de archivo → fixture nueva `extraccion-remito.json` (tipo REMITO, fecha estática 2026-11-07 — R0 corta antes de R5, sin riesgo de vencimiento) para ejercitar la admisión R0 desde la UI; (b) 2 PDFs fixture commiteados en `qa/e2e/fixtures/` (`pdf-escaneado-grafico.pdf` sin capa de texto, `factura-11-paginas.pdf` con 11 páginas) generados por `backend/scripts/generar_fixtures_e2e.py` (reportlab, dependencia ya declarada); (c) escenarios 9–10 de errores con `page.route` (abort → `ERROR_RED`; fulfill 502 → `EXTRACCION_FALLIDA`): el backend nunca recibe esas llamadas (0 créditos) y se aserta CU-05 (resultado previo conservado). El E2E de red/502 no toca backend ni reglas; el caso R0 ya estaba probado a nivel dominio (test_engine CU-06). No cambia contrato API, esquema de BD ni reglas de negocio. | 10/10 passed en 2 pasadas consecutivas (1.3 m / 34.4 s), `retries: 0`; pytest 110 passed (mock routing cubierto por test unitario), cobertura de `infrastructure/llm` 100%. |
| 2026-11-13 | **ADR-05-09:** puertos exclusivos del E2E (backend :8010, frontend :5175) + `reuseExistingServer: false` | Bug de operación detectado por Kevin en el escenario 2: con el backend manual corriendo en `:8000` en modo `llm`, `reuseExistingServer` (default local) hacía que el E2E lo reutilizara → la matriz de verdad mock no aplicaba (R3 comparaba $270.000/$285.000 reales vs los $28.200/$30.000 de la fixture) y el test fallaba (además de gastar créditos y tocar la BD real). Fix: puertos exclusivos + el proxy del frontend configurable por `VITE_PROXY_TARGET` (default `:8000` intacto para uso manual). Herramienta de desarrollo, sin cambios de contrato API/esquema/reglas. | 10/10 passed × 2 pasadas (52 s / 35.1 s) **con el backend manual llm corriendo en :8000 en paralelo**; el E2E nunca vuelve a depender del estado de la máquina del desarrollador. |
| 2026-11-13 | **ADR-05-10:** k6 funcional (`qa/load/funcional.js`) — correctitud del contrato bajo carga, separado del test de saturación | Kevin pidió además pruebas k6 **funcionales**: el smoke de estrés solo mide códigos HTTP; un 200 con JSON malformado pasaría. Script con 3 escenarios elegibles por `ESCENARIO` (`contrato`: 6 endpoints con asserts de contenido; `matriz`: matriz de verdad + remito fixture del E2E como fuente única — reutiliza `qa/e2e/fixtures/remito-transporte-2026.pdf`; `errores`: los 4 caminos 422/413/404 del contrato §3), `SMOKE=1` para CI y threshold `checks` > 99% con `http_req_failed` por escenario (en `errores` todos los requests son 4xx esperados). Carga moderada con **pausa 1 s por iteración**: a 14 VUs sin pausa satura el lock de la SQLite (p95 > 500 ms) — esa medición corresponde a `stress_test.js` (ADR-05-06). Herramienta de QA, sin cambios de contrato API/esquema/reglas. | Corrida completa 2 m: EXIT=0, 7008 requests, `http_req_failed` 0.00% en contrato y matriz (10.5% global = 4xx esperados de `errores`), p95 337 ms < 500. Smoke 30 s EXIT=0; los 3 escenarios individuales EXIT=0; `ESCENARIO` inválido → error claro EXIT=107. CI: stage nuevo tras k6 smoke (`SMOKE=1 k6 run qa/load/funcional.js`, reutiliza el backend mock del job). |

## 5. Criterio de Aceptación Final (Definition of Done) — Proyecto Completo

- [x] Todas las tareas de `03-tasks.md` de **los 6 módulos** están marcadas como `[x]`. *(Cerrado 2026-11-15: T-14..T-16 ejecutadas por Kevin — deploy Render + Vercel con smoke en verde; barrido de los 6 `03-tasks.md` confirmó cero checkboxes pendientes.)*
- [x] Todos los tests de Pytest pasan en verde (`unit` + `integration`, < 30 s, sin red). *(104 passed en 5.47 s.)*
- [x] Cobertura: dominio 100%, aplicación > 90% (gate activo). *(Dominio 100%, aplicación 100%, total 99.30% con `--cov-fail-under=95`.)*
- [x] Los tests de Playwright se ejecutan correctamente sin flakiness (2 pasadas). *(Con el escenario 5 de subida propia: 5/5 en 2 pasadas consecutivas (33,5 s / 31,3 s), `retries: 0`; antes, 4/4 en 3 pasadas.)*
- [x] k6 cumple con los SLAs de latencia (p95 < 500 ms) y tasa de error (< 1%) con 50 VUs en modo mock. *(0.00% errores, p95 449.35 ms — §3.)*
- [x] Los 3 PDFs de ejemplo son válidos y vigentes (fechas dentro de los 60 días de R5). *(Generados el 2026-11-12 con hoy−5/−20/−30; regenerar `scripts/generar_ejemplos.py` si la demo envejece — lo mismo aplica a la fecha estática de las fixtures del mock.)*
- [x] La demo completa corre de cero con 2 comandos (backend + frontend) en < 15 s de setup post-instalación. *(Quickstart del README raíz.)*
- [x] `specs/README.md` refleja el estado real (🟢 Completado) y cada `04-verification.md` tiene su ADR log completo. *(2026-11-15: MOD-05 → 🟢 tras el deploy; los 6 módulos 🟢 y los ADR logs completos — ADR-02-01..12, ADR-03-01..08, ADR-04-01..07, ADR-05-01..10.)*
- [x] Backend y frontend desplegados (Render + Vercel) con smoke post-deploy en verde y URLs documentadas. *(Hecho 2026-11-15: https://sofredoc-api.onrender.com (Render) + https://sofredoc.vercel.app (Vercel); smoke por Kevin en vivo — health 200, matriz de verdad completa, semáforo, JSON inspector e historial; ambos modos (`mock`/`llm`) verificados, queda `mock`. URLs y notas operativas en README raíz §"Producción"; guía en `docs/despliegue.md`.)*
- [x] `README.md` raíz con quickstart, arquitectura, sección de calidad y capturas de la demo. *(Capturas reales del E2E en `docs/capturas/`.)*
