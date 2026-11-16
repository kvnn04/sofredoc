# ADR-02-11: Letra de comprobante y Transparencia Fiscal Ley 27.743

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/02-extraccion-ia/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-14 |
| **Módulo** | MOD-02 — Ingesta PDF y Extracción IA |
| **Categoría** | Semántica fiscal |

## Decisión

letra del comprobante + Regla de Transparencia Fiscal (Ley 27.743) en B/C

## Motivo / Contexto

Segundo falso positivo con LLM real (Factura B real: ítems $340.000 + $185.000 + $95.000 = $620.000 con IVA incluido, total $620.000, recuado informativo 'IVA Contenido (Ley 27.743): $107.603,31'): el LLM cargaba `impuestos = 107603.31` desde ese dato informativo → R3 calculaba 620.000 + 107.603,31 ≠ 620.000 → DISCREPANCIA_CONTABLE. El recuado de Transparencia Fiscal es un desglose informativo YA INCLUIDO en el total (no se adiciona). Fix solo de extracción (R3 intacta): campo opcional `letra_comprobante` (str | null, patrón string | null probado en strict; ancla la regla por letra) + descripciones reescritas por letra (A: netos + impuestos = impuestos discriminados adicionados; B/C: importes finales con IVA incluido, `impuestos = 0` salvo percepciones/tributos adicionados) + regla explícita de NO cargar 'IVA Contenido' / 'Otros Impuestos Nacionales Indirectos' (Ley 27.743) + SYSTEM_PROMPT reestructurado por letra (ancla primero) + reintento reforzado. Fixture `extraccion-factura-b-transparencia.json` + 4 tests (letra B, impuestos 0, R3 verde, motor APROBADO con OC — total > $500.000 exige OC y la trae). Verificación con LLM real: **5/5 casos** (Factura B → APROBADO intento 1 con `letra=B, impuestos=0`; Factura A re-verificada como regresión → APROBADO con `letra=A, impuestos=74130`; matriz intacta). 119 tests en verde (99.59%), ruff verde, build frontend ✓ (espejo `types.ts` con `letra_comprobante`).

## Impacto

Invariante R3 intacto: `impuestos` = solo tributos que se adicionan a los subtotales. La letra es ancla de extracción + trazabilidad en el JSON inspector; ninguna regla la consume.
