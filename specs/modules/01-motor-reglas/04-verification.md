# VERIFICATION-01: Dominio y Motor de Reglas — Testing y Cierre

> **Audiencia:** QA, Lead Developer, CI/CD.

## 1. Pruebas Unitarias e Integración (Pytest)

```bash
# Correr pruebas de dominio y reglas
pytest backend/tests/unit -v

# Cobertura del dominio (gate: 100%)
pytest backend/tests/unit --cov=src/domain --cov-report=term-missing
```

### Cobertura Mínima Requerida
- Domain (models, value_objects, rules): **100%**
- Rendimiento: evaluación del engine con factura de 20 ítems en **< 10 ms** (test de referencia opcional con `time.perf_counter`).

### Matriz de Casos Borde Obligatoria (cada fila = 1 test)

| # | Regla | Entrada | Esperado |
| :--- | :--- | :--- | :--- |
| 1 | R1 | `30-12345678-1` (con guiones) | ✅ |
| 2 | R1 | `30123456781` (sin guiones) | ✅ |
| 3 | R1 | `30-12345678-9` (DV incorrecto) | ❌ `ERROR_CUIT_INVALIDO` |
| 4 | R1 | `30-12345678` (10 dígitos) | ❌ `ERROR_CUIT_INVALIDO` |
| 5 | R1 | CUIT con letras / vacío | ❌ `ERROR_CUIT_INVALIDO` |
| 6 | R1 | CUIT cuyo cálculo cae en dv=0 (resto 11) | ✅ (rama dv==11) |
| 7 | R1 | CUIT cuyo cálculo cae en dv=9 (resto 10) | ✅ (rama dv==10) |
| 8 | R2 | CUIT registrado activo | ✅ |
| 9 | R2 | CUIT ausente del padrón | ❌ `PROVEEDOR_NO_REGISTRADO` |
| 10 | R2 | CUIT registrado con `activo=false` | ❌ `PROVEEDOR_NO_REGISTRADO` |
| 11 | R3 | Desvío de exactamente **$1.00** | ✅ (dentro de tolerancia) |
| 12 | R3 | Desvío de **$1.01** | ❌ `DISCREPANCIA_CONTABLE` |
| 13 | R3 | Desvío negativo (total menor que suma) | ❌ con `detalles` con ambos montos |
| 14 | R4 | `monto_total = 500000.00` sin OC | ✅ (tope es estricto `>`) |
| 15 | R4 | `monto_total = 500000.01` sin OC | ❌ `FALTA_ORDEN_COMPRA` |
| 16 | R4 | `monto_total = 725000.00` **con** OC (`"OC-2026-001"`) | ✅ |
| 17 | R4 | OC con string vacío o solo espacios con tope excedido | ❌ `FALTA_ORDEN_COMPRA` |
| 18 | R5 | `fecha_emision = hoy` | ✅ |
| 19 | R5 | `fecha_emision = hoy - 60 días` | ✅ (no supera 60) |
| 20 | R5 | `fecha_emision = hoy - 61 días` | ❌ `COMPROBANTE_VENCIDO` (vencida) |
| 21 | R5 | `fecha_emision = mañana` | ❌ `COMPROBANTE_VENCIDO` (futura) |
| 22 | Engine | Factura que falla R3 y R5 a la vez | ❌ `RECHAZADO` con **ambos** códigos y 5 reglas reportadas |
| 23 | R0 | `tipo_comprobante="REMITO"` (resto válido) | ❌ `REMITO_NO_AUDITABLE` con **solo** la fila R0 (R1–R5 no se evalúan) |
| 24 | R0 | `tipo_comprobante="FACTURA"` | R0 no aparece: corre la evaluación completa R1–R5 |

## 2. Pruebas E2E (Playwright)

No aplica (módulo sin superficie HTTP propia; se cubre vía MOD-03/MOD-05).

## 3. Pruebas de Estrés y Rendimiento (k6)

No aplica en este módulo.

## 4. Registro de Decisiones de Arquitectura (ADR Log)

> **Índice maestro:** todas las decisiones del proyecto —numeradas y de base— están catalogadas en el índice [`adr/README.md`](../../adr/README.md). El texto completo vive en [`specs/adr/`](../../adr/): las decisiones de base de este módulo en el consolidado [`base-00-01-core-y-reglas.md`](../../adr/base-00-01-core-y-reglas.md). Esta sección queda como tabla resumen de navegación.

### Decisiones de base (sin ID)

Texto completo (motivo e impacto): [`base-00-01-core-y-reglas.md` · MOD-01](../../adr/base-00-01-core-y-reglas.md#mod-01-dominio-y-motor-de-reglas)

| Fecha | Decisión |
| :--- | :--- |
| 2026-11-12 | `Decimal` en el dominio (no `float`) |
| 2026-11-12 | Variante Módulo 11: dv=11→0, dv=10→9 |
| 2026-11-12 | Evaluación de las 5 reglas siempre completa |
| 2026-11-12 | `ClockPort` inyectable |
| 2026-11-12 | Reloj de sistema en `America/Argentina/Buenos_Aires` |
| 2026-11-12 | Regla de admisión R0 (remitos) |
| 2026-11-12 | Dependencia `tzdata` con marcador `sys_platform == "win32"` |
| 2026-11-12 | Sintaxis `X \| None` (PEP 604) + `collections.abc.Sequence` |
| 2026-11-12 | `Proveedor` definido en `domain/ports/padron_port.py` |
| 2026-11-12 | `digito_verificador_valido` retorna `False` si el formato es inválido |
| 2026-11-12 | `detalles` tipado `dict[str, str]`; montos es-AR vía `formato_ars` |
| 2026-11-12 | Fixture factory `factura(**overrides)` en `tests/unit/conftest.py` |

## 5. Criterio de Aceptación Final (Definition of Done)

- [x] Todas las tareas de `03-tasks.md` están marcadas como `[x]`.
- [x] Todos los tests de Pytest pasan en verde (50 passed, 2026-11-12).
- [x] Cobertura de `backend/src/domain/` = **100%** (`--cov-fail-under=100` en verde).
- [x] La matriz de casos borde (§1) está cubierta fila por fila (filas 1–24).
- [x] Ningún archivo de `domain/` importa `fastapi`, `sqlite3`, `pypdf` ni SDKs de LLM (verificación por grep: sin coincidencias).
