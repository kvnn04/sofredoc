# ADR-03-03: Conexión SQLite con threading.Lock y cierre en lifespan

> **Volver:** [Índice maestro de ADRs](../ADRs.md) · [§4 del módulo de origen](../modules/03-api-sqlite/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-03 — API REST y SQLite |
| **Categoría** | Dominio, datos y arquitectura |

## Decisión

conexión SQLite con `threading.Lock` + `cerrar()` en lifespan

## Motivo / Contexto

Los endpoints sync corren en el threadpool de FastAPI; el lock serializa el acceso a la conexión compartida y el cierre evita `ResourceWarning`.

## Impacto

Sin cambios de contrato; robustez bajo concurrencia.
