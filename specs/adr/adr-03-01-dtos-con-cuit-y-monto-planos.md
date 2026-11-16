# ADR-03-01: DTOs con cuit_emisor y monto_total planos

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/03-api-sqlite/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-03 — API REST y SQLite |
| **Categoría** | API y contratos |

## Decisión

DTOs con `cuit_emisor` y `monto_total` planos

## Motivo / Contexto

El diseño §2 (esencia) solo los lleva dentro de `datos_extraidos`; el listado del historial los necesita accesibles sin traer `datos_extraidos` completo (y en `ERROR_EXTRACCION` esos datos son NULL).

## Impacto

Campos adicionales (aditivos, no rompen el contrato §3).
