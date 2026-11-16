# ADR-02-02: Errores de extracción en el dominio

> **Volver:** [Índice maestro de ADRs](../ADRs.md) · [§4 del módulo de origen](../modules/02-extraccion-ia/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-02 — Ingesta PDF y Extracción IA |
| **Categoría** | Dominio, datos y arquitectura |

## Decisión

errores de extracción en `domain/errors.py`

## Motivo / Contexto

El DESIGN los llamaba "de infra", pero `application/` y `presentation/` deben capturarlos sin importar adaptadores concretos. Excepciones puras con atributo `codigo`.

## Impacto

MOD-03 mapea `error.codigo` a HTTP (422/502).
