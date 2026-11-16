# ADR-02-10: Semántica AFIP en el esquema y el prompt

> **Volver:** [Índice maestro de ADRs](../ADRs.md) · [§4 del módulo de origen](../modules/02-extraccion-ia/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-14 |
| **Módulo** | MOD-02 — Ingesta PDF y Extracción IA |
| **Categoría** | Semántica fiscal |

## Decisión

semántica AFIP en el esquema y el prompt — Factura A con IVA discriminado

## Motivo / Contexto

Falso positivo con LLM real (reportado por Kevin con una Factura A real: neto $353.000, IVA 21% $74.130, 'Importe Otros Tributos' $0, total $427.130): el LLM devolvía `impuestos = 0` — el campo no tenía descripción y el prompt decía "impuestos faltante es 0", así que el modelo casaba el campo con la fila 'Importe Otros Tributos' → R3 rechazaba DISCREPANCIA_CONTABLE por $74.130. Fix solo de extracción (R3 intacta): `Field(description=...)` AFIP en `impuestos`, `items[].subtotal`, `items[].precio_unitario` y `monto_total` (las description viajan al JSON Schema strict — verificado con test) + SYSTEM_PROMPT con reglas explícitas (subtotales/precios netos vs 'Subtotal c/IVA'; impuestos = suma de TODOS los impuestos discriminados al pie; solo 0 en Factura B/C) + reintento reforzado. Fixture `data/fixtures/extraccion-factura-a-iva.json` (solo JSON sintético, decisión de Kevin; el PDF real queda fuera del repo) + 4 tests nuevos. Verificación con LLM real: **4/4 casos** (Factura A → APROBADO en intento 1; matriz de verdad intacta); 115 tests en verde (99.59%), ruff verde.

## Impacto

La IA sigue sin decidir (RN-2-06): solo se aclara qué campo es cuál; la matemática sigue en R3 con ± $1.00. El mock es inmune (fixtures estáticas) — este bug solo era visible en modo `llm`.
