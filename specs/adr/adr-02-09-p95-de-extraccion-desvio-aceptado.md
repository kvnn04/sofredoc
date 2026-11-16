# ADR-02-09: p95 de extracción real y desvío de latencia aceptado

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/02-extraccion-ia/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-13 |
| **Módulo** | MOD-02 — Ingesta PDF y Extracción IA |
| **Categoría** | Operación y deploy |

## Decisión

p95 de extracción real > 8 s (umbral no cumplido)

## Motivo / Contexto

10 extracciones reales consecutivas: mediana 3.103 ms, pero outliers de 10.4 y 10.8 s (varianza de respuesta del proveedor `gpt-4o-mini` con Structured Outputs). PoC acepta el desvío: el umbral era de laboratorio; la latencia depende del proveedor, no del código (el motor de reglas sigue en < 10 ms). No cambia contrato API ni reglas de negocio.

## Impacto

p95 real ≈ 10.8 s — documentado; si la PoC lo exige, evaluar `gpt-4o` / timeout en el cliente (fuera de alcance MVP).
