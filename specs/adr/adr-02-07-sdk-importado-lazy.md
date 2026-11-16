# ADR-02-07: SDK importado lazy con umbral de caracteres significativos

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/02-extraccion-ia/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-02 — Ingesta PDF y Extracción IA |
| **Categoría** | Extracción IA |

## Decisión

SDK importado en perezoso + umbral de "significativos"

## Motivo / Contexto

El modo mock y los tests no requieren `openai` instalado (client.py lo importa dentro de la función). "20 caracteres significativos" = caracteres sin espacios (`"".join(texto.split())`).

## Impacto

Mock cero-dependencia; umbral determinista.
