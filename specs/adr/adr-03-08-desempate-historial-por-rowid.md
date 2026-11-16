# ADR-03-08: Desempate del historial por rowid DESC

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/03-api-sqlite/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-13 |
| **Módulo** | MOD-03 — API REST y SQLite |
| **Categoría** | Dominio, datos y arquitectura |

## Decisión

desempate del listado del historial por `rowid DESC` (`ORDER BY creado_en DESC, rowid DESC`)

## Motivo / Contexto

Bug de CI detectado en el E2E escenario 4: `creado_en` tiene precisión de segundos y en el runner (rápido, ~1,3 s/test) las auditorías del escenario 2 y 3 cayeron en el mismo segundo → el `ORDER BY creado_en DESC` sin desempate devolvía empates en orden indefinido y la UI cargó como "más reciente" la auditoría del escenario 2 (R3) en vez de la del escenario 3 (R4). El contrato CU-04 ("el más nuevo primero") se mantiene: con empate de segundo, el más nuevo es el último insertado (`rowid` refleja el orden de inserción). Sin cambios de DDL, contrato API ni reglas.

## Impacto

pytest **111 passed** (+1 test de integración que reproduce el empate: 3 filas mismo segundo → orden de inserción invertido, determinístico); cobertura total 99.59% (gate ≥95%). E2E re-verificado en verde tras el fix.
