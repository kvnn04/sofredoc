# ADR-05-02: Reset de BD efímera dentro del comando del webServer

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/05-qa-testing/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-05 — QA: Pytest, Playwright & k6 |
| **Categoría** | QA y CI |

## Decisión

reset de la BD efímera dentro del comando del `webServer` (`qa/e2e/reset-db.mjs`)

## Motivo / Contexto

Playwright arranca los `webServer` **antes** del `globalSetup`: borrar la BD ahí fallaba con EPERM (archivo abierto por uvicorn).

## Impacto

Cada corrida E2E empieza de cero (reproducible); RN-5-05 intacta.
