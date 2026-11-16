# ADR-02-04: Fallo del proveedor se tipifica y no se reintenta

> **Volver:** [Índice maestro de ADRs](../ADRs.md) · [§4 del módulo de origen](../modules/02-extraccion-ia/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-02 — Ingesta PDF y Extracción IA |
| **Categoría** | Extracción IA |

## Decisión

fallo del proveedor se tipifica en `client.py` y NO se reintenta

## Motivo / Contexto

El reintento es exclusivamente sobre `ValidationError` (RN-2-03, CU-03); reintentar errores del proveedor duplicaría costo/latencia.

## Impacto

`ExtraccionFallidaError` inmediata al fallar la API.
