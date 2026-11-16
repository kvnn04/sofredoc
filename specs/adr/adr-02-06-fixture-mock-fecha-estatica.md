# ADR-02-06: Fixture mock con fecha estática

> **Volver:** [Índice maestro de ADRs](../ADRs.md) · [§4 del módulo de origen](../modules/02-extraccion-ia/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-02 — Ingesta PDF y Extracción IA |
| **Categoría** | Operación y deploy |

## Decisión

fixture mock con fecha estática

## Motivo / Contexto

T-04 pide fecha "hoy − 5 días al momento de crear el fixture": se hornea `2026-11-07`. Riesgo conocido: tras 60 días (≈ 2027-01-06) la demo `aprobada` pasaría a RECHAZADO por R5 → regenerar fecha del fixture antes de esa demo.

## Impacto

Demo mock APROBADO válida hasta ≈ 2027-01-06.
