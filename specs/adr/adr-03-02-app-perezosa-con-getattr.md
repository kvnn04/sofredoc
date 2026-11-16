# ADR-03-02: App construida perezosamente con __getattr__

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/03-api-sqlite/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-03 — API REST y SQLite |
| **Categoría** | API y contratos |

## Decisión

`app` de `main.py` se construye perezosamente (`__getattr__`)

## Motivo / Contexto

Importar `src.main` desde los tests no debe crear `data/sofredoc.db` real; `uvicorn src.main:app` sigue funcionando (verificado en el smoke manual).

## Impacto

DoD §5 b-2: los tests no tocan la BD real (smoke usa settings temporales).
