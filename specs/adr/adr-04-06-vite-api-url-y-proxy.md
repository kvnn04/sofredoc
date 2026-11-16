# ADR-04-06: VITE_API_URL vacío usa el proxy de Vite

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/04-frontend/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-12 |
| **Módulo** | MOD-04 — Frontend Clean Architecture |
| **Categoría** | API y contratos |

## Decisión

`VITE_API_URL` vacío → base `/api/v1` (proxy de Vite del MOD-00 T-07) en lugar de `http://localhost:8000/api/v1` directo.

## Motivo / Contexto

Respeta la convención del scaffold y evita CORS en desarrollo; en deploy (Vercel) se define `VITE_API_URL` absoluta.

## Impacto

Solo configuración del cliente; contrato API intacto.
