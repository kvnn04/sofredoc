# ADR-03-04: Errores vía handlers de excepción

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/03-api-sqlite/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-03 — API REST y SQLite |
| **Categoría** | API y contratos |

## Decisión

errores de presentación vía handlers de excepción (no `HTTPException`)

## Motivo / Contexto

El contrato §3 exige cuerpo `{"error": {...}}` sin el wrapper `detail` de FastAPI; los routers levantan `ErrorHTTPTipado` y el dominio `ErrorTipificado` se mapea por `codigo`.

## Impacto

Cuerpos de error idénticos a §3 en todos los endpoints.
