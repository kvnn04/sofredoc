# ADR-04-07: Verificación visual diferida a Playwright de MOD-05

> **Volver:** [Índice maestro de ADRs](../ADRs.md) · [§4 del módulo de origen](../modules/04-frontend/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-04 — Frontend Clean Architecture |
| **Categoría** | QA y CI |

## Decisión

verificación visual del checklist §2 diferida a la suite Playwright de MOD-05 (que automatiza estos 10 escenarios); en MOD-04 se verificaron a nivel API/contrato con HTTP real.

## Motivo / Contexto

No hay navegador/headless disponible sin agregar dependencias no declaradas (MOD-05 las declara).

## Impacto

Checklist §2 y DoD ítems 3–4 quedan a la pasada visual de Kevin o a MOD-05. **Cerrado:** suite de MOD-05 en verde (5/5 × 2 pasadas) — ver evidencia §2.
