# ADR-05-03: El E2E no aserta el render interno del visor

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/05-qa-testing/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-05 — QA: Pytest, Playwright & k6 |
| **Categoría** | QA y CI |

## Decisión

el E2E no aserta sobre el visor de PDF

## Motivo / Contexto

Chromium headless no renderiza PDFs en línea (iframe vacío); el flujo auditado es completo.

## Impacto

Limitación del navegador headless, no del producto; en navegador real el visor muestra el PDF.
