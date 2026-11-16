# ADR-05-09: Puertos exclusivos del E2E 8010 y 5175

> **Volver:** [Índice de ADRs](README.md) · [§4 del módulo de origen](../modules/05-qa-testing/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| | |
| :--- | :--- |
| **Fecha** | 2026-11-13 |
| **Módulo** | MOD-05 — QA: Pytest, Playwright & k6 |
| **Categoría** | QA y CI |

## Decisión

puertos exclusivos del E2E (backend :8010, frontend :5175) + `reuseExistingServer: false`

## Motivo / Contexto

Bug de operación detectado por Kevin en el escenario 2: con el backend manual corriendo en `:8000` en modo `llm`, `reuseExistingServer` (default local) hacía que el E2E lo reutilizara → la matriz de verdad mock no aplicaba (R3 comparaba $270.000/$285.000 reales vs los $28.200/$30.000 de la fixture) y el test fallaba (además de gastar créditos y tocar la BD real). Fix: puertos exclusivos + el proxy del frontend configurable por `VITE_PROXY_TARGET` (default `:8000` intacto para uso manual). Herramienta de desarrollo, sin cambios de contrato API/esquema/reglas.

## Impacto

10/10 passed × 2 pasadas (52 s / 35.1 s) **con el backend manual llm corriendo en :8000 en paralelo**; el E2E nunca vuelve a depender del estado de la máquina del desarrollador.
