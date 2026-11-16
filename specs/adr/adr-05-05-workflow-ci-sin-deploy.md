# ADR-05-05: Workflow único de verificación sin deploy automático

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/05-qa-testing/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-05 — QA: Pytest, Playwright & k6 |
| **Categoría** | Operación y deploy |

## Decisión

workflow único de verificación, sin deploy automático

## Motivo / Contexto

SPEC-05 §5: el deploy de cierre es manual/scriptado; CI valida calidad en cada push.

## Impacto

Orden `pytest → ruff → build → playwright → k6 smoke` con reportes como artefactos.
