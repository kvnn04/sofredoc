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

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | `Decimal` en el dominio (no `float`) | Consistencia contable exacta; la tolerancia ±$1.00 y el borde $500.000 exigen precisión. | Serialización JSON explícita en MOD-03 (2 decimales). |
| 2026-11-12 | Variante Módulo 11: dv=11→0, dv=10→9 | Implementación AFIP de uso común; se documenta y queda fijada por tests (filas 6–7). | Cualquier desvío futuro requiere ADR + actualización de tests. |
| 2026-11-12 | Evaluación de las 5 reglas siempre completa | El operador necesita ver todos los desvíos de un vistazo (CU-06 del spec). | Sin cortocircuito; costo trivial (<10 ms). |
| 2026-11-12 | `ClockPort` inyectable | R5 depende de "hoy"; inyectarlo elimina mocks de tiempo y flakes. | Tests pasan fecha fija. |
| 2026-11-12 | Reloj de sistema en `America/Argentina/Buenos_Aires` | Confirmado por el product owner: la vigencia (R5) debe reflejar el día local del operador aunque el server corra en UTC. | `RelojSistema` usa `zoneinfo`; evita corrimientos de ±1 día. |
| 2026-11-12 | Regla de admisión R0 (remitos) | Confirmado por el product owner: un remito sin importes no admite R3/R4; se rechaza explícitamente en vez de inventar validaciones. | Cortocircuito **antes** de R1–R5; única excepción al "sin cortocircuito" de las 5 reglas. |

## 5. Criterio de Aceptación Final (Definition of Done)

- [ ] Todas las tareas de `03-tasks.md` están marcadas como `[x]`.
- [ ] Todos los tests de Pytest pasan en verde.
- [ ] Cobertura de `backend/src/domain/` = **100%**.
- [ ] La matriz de casos borde (§1) está cubierta fila por fila.
- [ ] Ningún archivo de `domain/` importa `fastapi`, `sqlite3`, `pypdf` ni SDKs de LLM (verificación por grep/lint).
