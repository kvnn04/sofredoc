# ADR-02-03: Esquema estricto con preparar_esquema_estricto

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/02-extraccion-ia/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-02 — Ingesta PDF y Extracción IA |
| **Categoría** | Extracción IA |

## Decisión

`preparar_esquema_estricto()` en `client.py`

## Motivo / Contexto

El JSON Schema de Pydantic (`title`, `default`, `minItems`, `minLength`, `minimum`) es rechazado por el modo `strict` del proveedor; se quitan claves no soportadas, se exige `required` completo y `additionalProperties: false`. Las restricciones reales las aplica Pydantic (RN-2-03).

## Impacto

Esquema compatible con Structured Outputs; probado contra el esquema real.
