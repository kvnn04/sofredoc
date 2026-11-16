# ADR-04-05: Espejo de tipos ajustado al contrato real de la API

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/04-frontend/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-04 — Frontend Clean Architecture |
| **Categoría** | API y contratos |

## Decisión

espejo de tipos ajustado al contrato real de la API (`url_pdf` en `Ejemplo`, `cuit_emisor`/`monto_total` planos, `detalles` en reglas, `R0` incluido, `resultado_esperado: string`, montos `number`).

## Motivo / Contexto

DESIGN-04 §2 pedía "fuente única: la API"; los DTOs reales de MOD-03 (fuente de verdad verificada por HTTP) difieren levemente del boceto del design.

## Impacto

Los componentes renderizan el contrato real; sin cambios de backend.
