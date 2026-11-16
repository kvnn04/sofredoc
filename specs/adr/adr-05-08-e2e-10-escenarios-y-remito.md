# ADR-05-08: E2E extendido a 10 escenarios con fixture REMITO

> **Volver:** [Índice maestro de ADRs](../ADRs.md) · [§4 del módulo de origen](../modules/05-qa-testing/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-13 |
| **Módulo** | MOD-05 — QA: Pytest, Playwright & k6 |
| **Categoría** | QA y CI |

## Decisión

extensión del E2E a 10 escenarios + fixture REMITO en el MockExtractor

## Motivo / Contexto

Kevin pidió ≥ 5 casos nuevos. Se agregan: (a) marca `"remito"` en el nombre de archivo → fixture nueva `extraccion-remito.json` (tipo REMITO, fecha estática 2026-11-07 — R0 corta antes de R5, sin riesgo de vencimiento) para ejercitar la admisión R0 desde la UI; (b) 2 PDFs fixture commiteados en `qa/e2e/fixtures/` (`pdf-escaneado-grafico.pdf` sin capa de texto, `factura-11-paginas.pdf` con 11 páginas) generados por `backend/scripts/generar_fixtures_e2e.py` (reportlab, dependencia ya declarada); (c) escenarios 9–10 de errores con `page.route` (abort → `ERROR_RED`; fulfill 502 → `EXTRACCION_FALLIDA`): el backend nunca recibe esas llamadas (0 créditos) y se aserta CU-05 (resultado previo conservado). El E2E de red/502 no toca backend ni reglas; el caso R0 ya estaba probado a nivel dominio (test_engine CU-06). No cambia contrato API, esquema de BD ni reglas de negocio.

## Impacto

10/10 passed en 2 pasadas consecutivas (1.3 m / 34.4 s), `retries: 0`; pytest 110 passed (mock routing cubierto por test unitario), cobertura de `infrastructure/llm` 100%.
