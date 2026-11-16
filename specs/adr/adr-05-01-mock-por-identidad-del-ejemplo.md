# ADR-05-01: Mock resuelve fixture por identidad del ejemplo

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/05-qa-testing/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-05 — QA: Pytest, Playwright & k6 |
| **Categoría** | QA y CI |

## Decisión

el mock resuelve la fixture por identidad del ejemplo (nombre de archivo `ej-…` o el PDF original re-subido)

## Motivo / Contexto

Los E2E (RN-5-04) corren en modo mock sin `LLM_API_KEY`: sin esto los 3 ejemplos darían APROBADO y los escenarios R3/R4 serían imposibles. No cambia contrato API, esquema de BD ni reglas de negocio.

## Impacto

Matriz de verdad reproducible en demo y E2E (T-06); fixture nueva `extraccion-monto-alto-sin-oc.json` con fecha estática 2026-10-13 (mismo riesgo de vencimiento que ADR-02-06: regenerar si la demo envejece).
