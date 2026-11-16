# ADR-05-06: Cuello de botella en el lock de SQLite a 50 VUs

> **Volver:** [Índice maestro de ADRs](../ADRs.md) · [§4 del módulo de origen](../modules/05-qa-testing/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-05 — QA: Pytest, Playwright & k6 |
| **Categoría** | Dominio, datos y arquitectura |

## Decisión

p95 de 449 ms a 50 VUs, cerca del umbral

## Motivo / Contexto

Cuello de botella: la conexión SQLite compartida con lock serializa inserts y lecturas (la extracción mock tarda < 10 ms).

## Impacto

Aceptable para la PoC; escalar a Postgres/pool de conexiones queda fuera de alcance (nota de DESIGN-05 §5).
