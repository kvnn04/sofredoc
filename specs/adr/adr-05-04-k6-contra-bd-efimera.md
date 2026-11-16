# ADR-05-04: k6 corre contra BD efímera en artifacts

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/05-qa-testing/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-05 — QA: Pytest, Playwright & k6 |
| **Categoría** | QA y CI |

## Decisión

k6 corre contra BD efímera `qa/artifacts/k6-sofredoc.db`

## Motivo / Contexto

RN-5-05: ningún test de carga toca `backend/data/sofredoc.db`.

## Impacto

Medición sobre SQLite en disco, igual que la corrida local.
