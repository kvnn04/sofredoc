# ADR-02-08: Decimal del esquema colapsado a rama numérica en strict

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/02-extraccion-ia/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-13 |
| **Módulo** | MOD-02 — Ingesta PDF y Extracción IA |
| **Categoría** | Extracción IA |

## Decisión

`Decimal` del esquema colapsado a rama numérica en strict

## Motivo / Contexto

Con LLM real, Pydantic genera `anyOf [{number}, {string}]` para `Decimal` y el proveedor elegía la rama string → montos formateados es-AR (`'$200.000,00'`) que Pydantic rechaza → `EXTRACCION_FALLIDA` en 2 intentos (bug solo visible con `EXTRACTOR_MODE=llm`; el mock devuelve números limpios). Fix: `preparar_esquema_estricto` colapsa ese anyOf a `{"type": "number"}` + prompt reforzado ("montos números sin $ ni separadores"). No cambia contrato API ni reglas. 109 tests en verde; cobertura `infrastructure/llm` 100%.

## Impacto

Montos siempre números JSON; validación final sigue siendo Pydantic (RN-2-03).
