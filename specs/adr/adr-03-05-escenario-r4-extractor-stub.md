# ADR-03-05: Escenario R4 probado con extractor stub

> **Volver:** [Índice maestro de ADRs](../ADRs.md) · [§4 del módulo de origen](../modules/03-api-sqlite/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-03 — API REST y SQLite |
| **Categoría** | QA y CI |

## Decisión

escenario R4 (`FALTA_ORDEN_COMPRA`) se prueba con extractor stub

## Motivo / Contexto

El mock solo trae variantes `aprobada`/`rechazado` (R3); la fila 3 de la matriz se verifica inyectando un extractor fijo en `create_app`. El flujo end-to-end real con LLM queda en la verificación pendiente de MOD-02 §2.

## Impacto

Sin cambios en `MOCK_VARIANT` ni en contratos.
