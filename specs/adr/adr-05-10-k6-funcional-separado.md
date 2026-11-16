# ADR-05-10: k6 funcional separado del de saturación

> **Volver:** [Índice maestro de ADRs](../ADRs.md) · [§4 del módulo de origen](../modules/05-qa-testing/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-13 |
| **Módulo** | MOD-05 — QA: Pytest, Playwright & k6 |
| **Categoría** | QA y CI |

## Decisión

k6 funcional (`qa/load/funcional.js`) — correctitud del contrato bajo carga, separado del test de saturación

## Motivo / Contexto

Kevin pidió además pruebas k6 **funcionales**: el smoke de estrés solo mide códigos HTTP; un 200 con JSON malformado pasaría. Script con 3 escenarios elegibles por `ESCENARIO` (`contrato`: 6 endpoints con asserts de contenido; `matriz`: matriz de verdad + remito fixture del E2E como fuente única — reutiliza `qa/e2e/fixtures/remito-transporte-2026.pdf`; `errores`: los 4 caminos 422/413/404 del contrato §3), `SMOKE=1` para CI y threshold `checks` > 99% con `http_req_failed` por escenario (en `errores` todos los requests son 4xx esperados). Carga moderada con **pausa 1 s por iteración**: a 14 VUs sin pausa satura el lock de la SQLite (p95 > 500 ms) — esa medición corresponde a `stress_test.js` (ADR-05-06). Herramienta de QA, sin cambios de contrato API/esquema/reglas.

## Impacto

Corrida completa 2 m: EXIT=0, 7008 requests, `http_req_failed` 0.00% en contrato y matriz (10.5% global = 4xx esperados de `errores`), p95 337 ms < 500. Smoke 30 s EXIT=0; los 3 escenarios individuales EXIT=0; `ESCENARIO` inválido → error claro EXIT=107. CI: stage nuevo tras k6 smoke (`SMOKE=1 k6 run qa/load/funcional.js`, reutiliza el backend mock del job).
