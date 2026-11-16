# ADR-02-01: OpenAI agregada a requirements.txt

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/02-extraccion-ia/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-02 — Ingesta PDF y Extracción IA |
| **Categoría** | Extracción IA |

## Decisión

`openai>=1.40` agregada a `requirements.txt`

## Motivo / Contexto

El design la declara (§4) pero faltaba en el archivo; **aprobado por Kevin** vía pregunta en sesión.

## Impacto

Instalada 3.49.0 en el venv.
