# Decisiones de base (sin ID) — MOD-00 y MOD-01: Core y Motor de Reglas

> **Volver:** [Índice maestro de ADRs](../ADRs.md) · [§4 MOD-00](../modules/00-monolito-core/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log) · [§4 MOD-01](../modules/01-motor-reglas/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

Consolidado de las **15 decisiones de base** (sin ID) de MOD-00 y MOD-01, con el texto verbatim del §4 de cada módulo (fecha, decisión, motivo e impacto intactos).

## MOD-00: Arquitectura Monolito y Core

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | Migrar de `backend/app/` plano a Clean Architecture `backend/src/` | La guía SDD exige separación de capas; el documento original era monolito plano de 5 archivos. | Mejor testabilidad; se documenta el mapeo en `specs/README.md`. |
| 2026-11-12 | `pypdf` como parser PDF del MVP | Liviano y suficiente para PDFs digitales estándar; `pdfplumber` queda como fallback documentado. | Menos dependencias; riesgo documentado en MOD-02. |
| 2026-11-12 | Sin ORM (`sqlite3` stdlib) | PoC con 1 tabla; mantener dependencias mínimas. | DDL manual en MOD-03. |

## MOD-01: Dominio y Motor de Reglas

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | `Decimal` en el dominio (no `float`) | Consistencia contable exacta; la tolerancia ±$1.00 y el borde $500.000 exigen precisión. | Serialización JSON explícita en MOD-03 (2 decimales). |
| 2026-11-12 | Variante Módulo 11: dv=11→0, dv=10→9 | Implementación AFIP de uso común; se documenta y queda fijada por tests (filas 6–7). | Cualquier desvío futuro requiere ADR + actualización de tests. |
| 2026-11-12 | Evaluación de las 5 reglas siempre completa | El operador necesita ver todos los desvíos de un vistazo (CU-06 del spec). | Sin cortocircuito; costo trivial (<10 ms). |
| 2026-11-12 | `ClockPort` inyectable | R5 depende de "hoy"; inyectarlo elimina mocks de tiempo y flakes. | Tests pasan fecha fija. |
| 2026-11-12 | Reloj de sistema en `America/Argentina/Buenos_Aires` | Confirmado por el product owner: la vigencia (R5) debe reflejar el día local del operador aunque el server corra en UTC. | `RelojSistema` usa `zoneinfo`; evita corrimientos de ±1 día. |
| 2026-11-12 | Regla de admisión R0 (remitos) | Confirmado por el product owner: un remito sin importes no admite R3/R4; se rechaza explícitamente en vez de inventar validaciones. | Cortocircuito **antes** de R1–R5; única excepción al "sin cortocircuito" de las 5 reglas. |
| 2026-11-12 | Dependencia `tzdata` con marcador `sys_platform == "win32"` | `zoneinfo("America/Argentina/Buenos_Aires")` no resuelve en Windows sin el paquete (T-13). Aprobado por Kevin en la sesión. | En Linux/Render no se instala (la base de zonas ya existe en el sistema). |
| 2026-11-12 | Sintaxis `X \| None` (PEP 604) y `collections.abc.Sequence` en vez de `Optional[X]`/`typing.Sequence` | Reglas `UP` de ruff (target py311); semántica idéntica a DESIGN-01 §2. | Sin impacto de contrato. |
| 2026-11-12 | `Proveedor` definido en `domain/ports/padron_port.py` (el design lo esbozaba dentro de rules/base.py) | T-03 (puerto + Proveedor) antecede a T-04; evita la dependencia ports→rules. | `rules/base.py` importa `Proveedor` desde el puerto. |
| 2026-11-12 | `digito_verificador_valido` retorna `False` si el formato es inválido | Guard defensivo: evita `ValueError` con letras/cadenas cortas al llamar el método directamente (matriz fila 5). | `es_valido()` conserva el cortocircuito del pseudocódigo. |
| 2026-11-12 | `detalles` tipado `dict[str, str]`; mensajes R3/R4 con montos es-AR vía helper `formato_ars` (`$25.000,00`) | Legibilidad para el operador, fiel al ejemplo de mensaje de DESIGN-01 §2. | JSON de MOD-03 no cambia (`detalles` sigue siendo string). |
| 2026-11-12 | Fixture factory `factura(**overrides)` en `tests/unit/conftest.py` (compartido por test_reglas y test_engine) | T-15 lo pedía dentro de test_reglas.py; el conftest evita duplicarlo en T-16. | Sin impacto en código de producción. |
