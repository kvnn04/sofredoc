# ADR-05-07: Estado de carga asertado con page route

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/05-qa-testing/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-05 — QA: Pytest, Playwright & k6 |
| **Categoría** | QA y CI |

## Decisión

el estado "Auditando…" del escenario 5 se aserta amplificando la latencia del `POST /auditar` con `page.route` (delay 800 ms); backend real intacto.

## Motivo / Contexto

La auditoría mock responde en < 10 ms: el estado de carga es demasiado breve para asertarlo de forma estable sin `retries` (RN-5-06). El delay se agrega solo en el navegador del test.

## Impacto

El E2E verifica spinner + botón deshabilitado + skeleton sin flake; también aserta que el visor recibe `iframe[src^="blob:"]` (RN-4-04) sin afirmar el render interno del PDF (ADR-05-03 se mantiene).
