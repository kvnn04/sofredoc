# ADR-03-07: Montos de datos_extraidos como número JSON

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/03-api-sqlite/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-03 — API REST y SQLite |
| **Categoría** | API y contratos |

## Decisión

montos de `datos_extraidos` como número (no string)

## Motivo / Contexto

pydantic v2 serializa `Decimal` como string en modo JSON; la convención global exige número con 2 decimales → conversor explícito en el caso de uso.

## Impacto

`monto_total: 384000.0` (número) en JSON, como en el ejemplo §3.
