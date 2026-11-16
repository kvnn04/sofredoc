# ADR-03-06: reportlab solo para el script de ejemplos

> **Volver:** [Índice maestro de ADRs](../ADRs.md) · [§4 del módulo de origen](../modules/03-api-sqlite/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-03 — API REST y SQLite |
| **Categoría** | QA y CI |

## Decisión

`reportlab` en requirements.txt

## Motivo / Contexto

Declarada por DESIGN-03 §4 como dependencia única del script `generar_ejemplos.py`; no se usa en `src/` (el dominio y los tests generan PDFs mínimos sin ella).

## Impacto

requirements.txt: `reportlab>=4.0`.
