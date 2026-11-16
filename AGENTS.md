# AGENTS.md — Contexto Maestro para Agentes de IA

> **Proyecto:** SofreDoc Validator (PoC Fullstack & Python/AI — Sofre Digital S.A.)
> **Propósito de este archivo:** darle a cualquier agente de IA el contexto mínimo y las reglas de trabajo para implementar este proyecto de forma eficiente, sin re-decisiones ni contradicciones.
> **Regla 0:** Leé este archivo **completo antes de escribir una línea de código**. Si algo de acá contradice tu intuición, gana este archivo (y las specs que referencia).

---

## 1. El proyecto en 30 segundos

Aplicación web IDP (Intelligent Document Processing) que audita facturas en PDF:

1. El usuario sube un PDF (o elige 1 de 3 ejemplos pre-cargados).
2. Se extrae el texto (`pypdf`) y un LLM con **Structured Outputs** lo convierte en un objeto tipado Pydantic (`FacturaExtraida`). **La IA solo extrae, nunca decide.**
3. Un **motor de reglas determinista en Python puro** (R0–R5) audita el objeto: CUIT, padrón, matemática, OC, vigencia.
4. El resultado (semáforo ✅/❌ + datos + JSON crudo + latencias) se muestra en una pantalla dividida React y se persiste en SQLite (historial).

**Stack:** Python 3.11+, FastAPI, Pydantic v2, SQLite (stdlib), React + TypeScript + Vite + Tailwind, pytest, Playwright, k6.
**Meta de entrega:** MVP funcional, demo evaluable en < 15 s de setup, tests en verde y deploy (Render + Vercel).

## 2. Fuente de verdad: `specs/`

| Documento | Qué contiene |
| :--- | :--- |
| `specs/README.md` | Índice maestro + **convenciones globales** (leer primero) |
| `specs/modules/00..05/01-spec.md` | Qué y por qué: reglas de negocio, casos de uso Given-When-Then, fuera de alcance |
| `specs/modules/00..05/02-design.md` | Cómo: Clean Architecture, modelos, DDL, contratos API, prompts |
| `specs/modules/00..05/03-tasks.md` | Plan atómico con checkboxes `[ ]` → `[x]` (tu checklist de trabajo) |
| `specs/modules/00..05/04-verification.md` | Tests obligatorios, matriz de casos borde, umbrales, **ADR Log** y DoD del módulo |
| `specs/ADRs.md` | **Índice maestro de ADRs**: las 33 decisiones numeradas + 38 de base, organizadas por tema, con link por ancla directa a cada ADR |
| `specs/PROGRESO.md` | **Bitácora de continuidad**: estado exacto del proyecto (leer SIEMPRE al arrancar) |

**Orden de implementación (dependencias estrictas):** `MOD-00` (core) → `MOD-01` (reglas) → `MOD-02` (extracción) → `MOD-03` (API/SQLite) → `MOD-04` (frontend) → `MOD-05` (QA + deploy).

**Regla de oro:** si tu código contradice una spec, **el código está mal**. Si la spec es incorrecta o ambigua → protocolo de desvíos (§5).

## 3. Protocolo de arranque de sesión (misión implícita — Kevin no escribe prompts largos)

Kevin te da **una palabra**; la misión completa está implícita acá.

### Mini-comandos (lo único que Kevin necesita escribir)

| Comando | Misión |
| :--- | :--- |
| **`arrancá`** | **Misión por defecto**: implementar el módulo pendiente **completo** (ver abajo) |
| `MOD-XX` | Override: ese módulo completo (ej. `MOD-02`) |
| `MOD-XX Fase N` | Override fino: solo esa fase (ej. `MOD-01 Fase 3`) |
| `prueba` | Solo la **próxima fase** pendiente (para probar rápido a un agente nuevo) |
| `estado` | Resumen del estado (bitácora + pendientes). No toca código ni commitea |
| `todo` | Modo continuo: módulo tras módulo hasta agotar pendientes o que Kevin diga basta |
| `DoD` | Revisión final global contra `specs/modules/05-qa-testing/04-verification.md` §5 |

### Ejecución de la misión por defecto (`arrancá`)

1. Leer `specs/README.md` (convenciones globales).
2. Leer `specs/PROGRESO.md` (bitácora: dónde quedó exactamente la sesión anterior; si hay trabajo a medio hacer, **continuarlo antes que empezar otra cosa**).
3. Verificar estado real: `git log --oneline -10` y revisar checkboxes `[ ]` pendientes en `specs/modules/*/03-tasks.md`.
4. Detectar el **módulo pendiente de menor ID** (orden MOD-00→05) y leer sus 4 archivos (`01-spec`, `02-design`, `03-tasks`, `04-verification`).
5. **Anunciar la misión en una línea** (ej. *"Misión: MOD-01 completo — motor de reglas R0–R5"*) y **ejecutar sin esperar confirmación** (preguntar solo si hay ambigüedad real con varias opciones igualmente válidas).
6. Implementar **fase por fase hasta cerrar el módulo completo**: tareas en orden estricto, marcar `[x]`, verificación completa con output real (§4), commit por fase.
7. Al cerrar el módulo: actualizar la bitácora (`specs/PROGRESO.md`), actualizar el estado del módulo en la tabla de `specs/README.md`, y **detenerse esperando a Kevin**. NO continuar con el módulo siguiente salvo orden explícita (otro `arrancá` o `todo`).

Si todo está `[x]` y no hay fases pendientes: informar que el proyecto está completo y proponer la revisión final del DoD global (MOD-05 §5) — ejecutarla solo si Kevin escribió `DoD`.

## 4. Protocolo de trabajo

- **Tareas en orden estricto** dentro del módulo; al completar cada tarea marcar su checkbox `[x]` en `03-tasks.md`.
- **Verificación completa:** antes de dar por cerrada una fase o módulo, ejecutar los comandos de `04-verification.md` de ese módulo y mostrar el **output real** (tests en verde, build, lint). Nunca declarar "listo" sin evidencia ejecutada.
- **Commits por fase** (convención, en español): `MOD-01 Fase 2: reglas R1–R5 + engine` — al cerrar cada fase del `03-tasks.md`. Sin `push` salvo orden explícita.
- **Desvíos (ADR + preguntar):** desvío menor o implementación ambigua → registrar en el **ADR Log** de `04-verification.md` del módulo (y sumar la fila al índice [`specs/ADRs.md`](./specs/ADRs.md)) y seguir. Si el desvío cambia **contrato API, esquema de BD o una regla de negocio** → **preguntar al usuario antes** de tocar código.
- **Specs primero:** cualquier cambio de spec se hace editando el `.md` correspondiente (+ entrada ADR), nunca solo en el código.
- **Estado global RECHAZADO = `200 OK`** (resultado de negocio). Los 4xx/5xx quedan reservados a fallos de contrato/infraestructura.

## 5. Autonomía concedida (por Kevin, 2026-11-12)

Podés hacer **sin preguntar**:
- Correr tests y builds (pytest, npm run build, ruff, playwright, k6 smoke).
- Instalar dependencias **ya declaradas** en `requirements.txt` / `package.json`.
- Crear y editar archivos del repo (código, tests, scripts, specs, bitácora).
- `git commit` local siguiendo la convención.
- Llamadas LLM reales (modo `llm`) — con key configurada; **registrar en la bitácora** cada tramo de prueba con LLM real (para control de costo).
- `git push` / deploy — solo hacia remotos/plataformas que Kevin haya configurado u ordenado explícitamente.

## 6. Decisiones firmes (no re-debatir, están en ADRs)

1. **Extracción IA:** OpenAI `gpt-4o-mini`, Structured Outputs con JSON Schema de Pydantic, `temperature=0`, máximo **1 reintento** sobre `ValidationError` o inconsistencia aritmética (gate = ecuación de R3, ADR-02-12). `impuestos` NO viaja al LLM: se calcula en Python desde `detalle_impuestos` (líneas del pie extraídas literal). `EXTRACTOR_MODE=mock` por default.
2. **Solo facturas auditable:** `REMITO` → regla de admisión **R0** rechaza con `REMITO_NO_AUDITABLE` sin evaluar R1–R5.
3. **CUIT Módulo 11:** pesos `[5,4,3,2,7,6,5,4,3,2]`; `dv = 11 - (suma % 11)`; `dv==11→0`, `dv==10→9`. Válidos de referencia: `30-12345678-1`, `30-71234567-1`, `20-12345678-6`; inválido: `30-12345678-9`.
4. **Reglas:** R3 tolerancia ± $1.00 · R4 tope estricto `> $500.000` exige OC · R5 vigencia 0–60 días (fecha futura rechaza; reloj en `America/Argentina/Buenos_Aires`).
5. **PDF:** ≤ 5 MB · máx **10 páginas** · sin capa de texto → `PDF_SIN_TEXTO` · campos críticos (CUIT/fecha) faltantes tras reintento → `EXTRACCION_FALLIDA` (502). Nunca auditar datos parciales.
6. **Latencia desglosada:** `latencia_extraccion_ms` (IA) + `latencia_reglas_ms` (motor) + `tiempo_ejecucion_ms` (total), persistidas en SQLite.
7. **Frontend:** pantalla dividida (visor iframe ~40% / resultados ~60%), sin router ni store global ni axios; JSON inspector muestra **Pydantic + crudo IA**.
8. **Entorno:** venv + `requirements.txt` (sin uv, sin ORM, sin docker). Git con commit por fase.
9. **Deploy (hecho 2026-11-15):** producción en https://sofredoc.vercel.app (Vercel) + https://sofredoc-api.onrender.com (Render); SQLite efímero en free tier (el historial se reinicia por deploy — documentado, aceptado). Modo actual `mock`; conmutar a `llm` en Render para evaluaciones con IA real (ambos modos verificados en producción).

## 7. Cheat sheet de contratos

**API base:** `/api/v1` · Backend `:8000` · Frontend `:5173`

| Método | Ruta | Nota |
| :--- | :--- | :--- |
| `POST` | `/api/v1/auditar` | multipart `file` (PDF ≤ 5 MB) → `ResultadoAuditoria` |
| `GET` | `/api/v1/ejemplos` | 3 ejemplos con `resultado_esperado` |
| `GET` | `/api/v1/ejemplos/{id}/pdf` | PDF crudo (`application/pdf`) |
| `GET` | `/api/v1/historial?limit=20&offset=0` | paginado, sin `json_crudo_ia` |
| `GET` | `/api/v1/historial/{id}` | detalle completo |
| `GET` | `/api/v1/health` | `{"status":"ok","extractor_mode":...}` |

**Códigos de regla:** R0 admisión · R1 `ERROR_CUIT_INVALIDO` · R2 `PROVEEDOR_NO_REGISTRADO` · R3 `DISCREPANCIA_CONTABLE` · R4 `FALTA_ORDEN_COMPRA` · R5 `COMPROBANTE_VENCIDO`. Las 5 se evalúan siempre (sin cortocircuito) excepto R0.
**Errores HTTP:** 413 `ARCHIVO_MUY_GRANDE` · 422 `PDF_INVALIDO` (incluye >10 páginas) / `PDF_SIN_TEXTO` · 502 `EXTRACCION_FALLIDA` · 404 `AUDITORIA_NO_ENCONTRADA` / `EJEMPLO_NO_ENCONTRADO`.
**Ejemplos (matriz de verdad):** `ej-factura-aprobada` → APROBADO · `ej-factura-desvio` → RECHAZADO (R3) · `ej-monto-alto-sin-oc` → RECHAZADO (R4).

**Estructura backend (Clean Architecture, obligatoria):**
```text
backend/src/
├── domain/           # Python puro: modelos, VOs, reglas, puertos (PROHIBIDO importar fastapi/sqlite3/pypdf/SDK LLM)
├── application/      # Casos de uso (AuditarComprobanteUseCase)
├── infrastructure/   # Adaptadores: db (SQLite), pdf (pypdf), llm (OpenAI/mock), padron (JSON), clock
└── presentation/     # Routers FastAPI + DTOs
```
Frontend espejo: `domain/ | application/ | infrastructure/ | presentation/` en `frontend/src/`.

## 8. Convenciones de código

- Dominio y reglas con **`Decimal`** (nunca `float` para montos); serialización JSON con 2 decimales.
- Fechas `ISO 8601`; timestamps UTC (`...Z`); reloj de negocio en `America/Argentina/Buenos_Aires`.
- Sin I/O ni red en tests unitarios: LLM falsificado (stub), SQLite temporal, fechas fijas vía `ClockPort`.
- Cobertura con gate: `domain/` **100%**, `application/` **> 90%** (`--cov-fail-under`).
- Spanish para documentación/mensajes de usuario/commits; identificadores de negocio en español (`FacturaExtraida`, `numero_orden_compra`).
- **Windows/PowerShell:** venv con `.venv\Scripts\Activate`; rutas con `\` o `/` en Python (usar `pathlib`).

## 9. Anti-patrones (NO hacer)

- ❌ Delegar cálculos o decisiones de negocio al LLM; ❌ "corregir" datos extraídos.
- ❌ Instalar dependencias fuera de las declaradas sin preguntar; ❌ pandas / ORM / axios / router / state manager.
- ❌ Secretos o `.env` real en el repo; ❌ push a remotos sin orden explícita.
- ❌ Cortocircuitar reglas de negocio (R1–R5 siempre se evalúan todas).
- ❌ Declarar algo verde sin haber corrido los comandos de verificación.
- ❌ Editar `specs/` solo para "adaptarla" al código ya escrito (eso va por ADR + pregunta).

## 10. Comandos de referencia (implementar según módulos)

```powershell
# Backend (desde backend/)
python -m venv .venv ; .\.venv\Scripts\Activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000

# Frontend (desde frontend/)
npm install ; npm run dev      # http://localhost:5173

# Calidad
pytest backend/tests -v --cov=src --cov-report=term-missing
npx playwright test qa/e2e/auditoria.spec.ts   # con backend(mock)+frontend arriba (usa puertos propios 8010/5175)
k6 run qa/load/stress_test.js                  # SOLO con EXTRACTOR_MODE=mock (saturación)
k6 run qa/load/funcional.js                    # SOLO con EXTRACTOR_MODE=mock (contrato/matriz/errores; SMOKE=1, ESCENARIO=…)
```

## 11. Checklist de cierre de sesión (obligatorio)

- [ ] Checkboxes `[x]` actualizados en el `03-tasks.md` del módulo.
- [ ] **Nueva entrada en `specs/PROGRESO.md`** (ver plantilla del archivo): qué se hizo, evidencia de verificación (resumen de outputs), estado exacto, próximos pasos concretos, ADRs nuevos.
- [ ] Commit por fase (`MOD-XX Fase N: ...`).
- [ ] Si un módulo cerró: actualizar su estado en la tabla de `specs/README.md`.
