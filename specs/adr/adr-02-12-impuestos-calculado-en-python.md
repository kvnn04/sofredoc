# ADR-02-12: Impuestos calculado en Python y gate de consistencia

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/02-extraccion-ia/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-14 |
| **Módulo** | MOD-02 — Ingesta PDF y Extracción IA |
| **Categoría** | Semántica fiscal |

## Decisión

`detalle_impuestos` línea a línea + `impuestos` calculado en Python + gate de consistencia pre-reintento

## Motivo / Contexto

Tercer falso positivo con LLM real (Factura A real con alícuotas mixtas: neto $800.000 — $360.000 al 21% + $440.000 al 10,5% —, IVA 21% $75.600, IVA 10,5% $46.200, Percepción IIBB ARBA 3% $24.000, total $945.800): el schema le pedía un único escalar `impuestos` y el modelo sumaba las 3 líneas **de memoria** → devolvió 94.600 (error aritmético de $51.200) → R3 rechazaba. Además `numero_comprobante` salía '00019384' sin el Punto de Venta. **Decisión preguntada a Kevin (5/5 recomendados):** (1) el recálculo vive en el dominio, (2) `impuestos` sale del schema del LLM, (3) fixtures mock intactas + fixture nueva, (4) `numero` solo semántica (sin normalizar en código), (5) verificación con LLM real. Implementación: modelo `ImpuestoDetalle {concepto, monto}` + `FacturaExtraida.detalle_impuestos: list[ImpuestoDetalle]` (una entrada por línea, extraída literal) + `model_validator` que recalcula `impuestos = Σ montos` en Python/Decimal cuando el detalle trae líneas (retrocompat: fixtures mock sin el campo conservan su literal) + `numero_comprobante` con description 'PPPPP-NNNNNNNN' (ej. '00005-00019384') + `esquema_para_llm()` en el extractor retira `impuestos` del JSON Schema (el modelo ya no puede errar la suma; trazabilidad línea a línea en el JSON crudo) + reglas de prompt: copiar dígito a dígito, excluir Ley 27.743 y **no duplicar** un tributo que figure en una tabla de desglose ('DETALLE DE OTROS TRIBUTOS / PERCEPCIONES') y también en la línea agregada 'Importe Otros Tributos' del pie (son EL MISMO monto). **Gate de consistencia pre-reintento (extensión de RN-2-03, aprobada por Kevin):** el extractor evalúa la MISMA ecuación de R3 vía nuevo helper de dominio `calculo_total()` (fuente única con `TOLERANCIA`, solo FACTURA — en REMITO decide R0); si el intento no cuadra (Σ items + impuestos ≠ total ± $1) reintenta con verificación aritmética reforzada; si ningún intento cuadra, sale el último validado y R3 decide (RECHAZADO = 200 OK, nunca se corrigen datos). Fixture `extraccion-factura-a-mixta.json` (datos reales del comprobante; fecha estática 2026-11-14, caducidad R5 ≈ 2027-01-13) + 7 tests nuevos (5 de dominio/motor + 2 de esquema) + 3 del gate (reintento por inconsistencia, ambos intentos inconsistentes → R3, REMITO immune). Verificación con LLM real (4 corridas ad-hoc): mixta real → intento 1 inconsistente (el gate detectó un resbalón de copia 46.000 por 46.200) → **intento 2 → `impuestos = 145.800`, `numero = '00005-00019384'`, R1–R5 OK → APROBADO**; matriz intacta (aprobada → APROBADO; desvío genuino → RECHAZADO R3 consumiendo su reintento; monto-alto → RECHAZADO R4). 129 tests en verde (99.61%), ruff verde, build frontend ✓ (espejo `types.ts` con `ImpuestoDetalle`).

## Impacto

Contrato `datos_extraidos` extendido de forma aditiva (`detalle_impuestos`, campo nuevo dentro del JSON) — aprobado por Kevin; sin cambios de DDL ni de reglas (R3 intacta, ahora con la ecuación compartida en `calculo_total`). `json_crudo_ia` deja de incluir `impuestos` (el campo es derivado; la trazabilidad del pie queda en `detalle_impuestos`). Costo real: una extracción inconsistente puede consumir su 2º intento (+1 llamada) — aceptado; RN-2-03 conserva el tope de 2 llamadas.
