# PROGRESO.md — Bitácora de Continuidad del Proyecto

> **Para todo agente de IA:** este archivo es tu punto de partida junto con `AGENTS.md`. Describe el estado **exacto** del proyecto. Al cerrar tu sesión, agregá una entrada nueva al final usando la plantilla de abajo. No edites ni borres entradas anteriores (el historial es trazabilidad).

---

## Estado actual (resumen rápido)

- **Fase del proyecto:** MOD-00..MOD-05 en lo esencial: MOD-00..MOD-04 completos (MOD-04 con DoD 5/5 tras automatizar su checklist en el E2E) + **MOD-05 QA completo (T-01..T-13 + T-06-bis)**: gate de cobertura, E2E Playwright (**10 escenarios** × 2 pasadas verdes: demo, subida propia, R0 remito, PDF_SIN_TEXTO, 11 páginas, red caída y 502 — ADR-05-08), k6 a 50 VUs en verde, workflow CI, README+capturas. Falta el **deploy de cierre (T-14..T-16)**.
- **Git:** ramas unificadas el 13/11 — `main` (ex-`master` renombrada, con merge fast-forward de `pruebaFront`) contiene todo el historial (MOD-00..MOD-05 Fase 4-bis, hasta `6db502d`); `remote origin` = https://github.com/kvnn04/sofredoc.git (orden de push explícita de Kevin; **la ejecución del push la hace Kevin**). `pruebaFront` queda apuntando al mismo commit (borrable).
- **Siguiente acción concreta:** (1) push de `main` a GitHub (lo ejecuta Kevin; el CI `.github/workflows/verificacion.yml` corre solo al pushear) → (2) deploy Render + Vercel siguiendo `docs/despliegue.md` (15–20 min) → (3) DoD global (`DoD`).
- **Módulos:** 00 🟢 · 01 🟢 · 02 🟢 · 03 🟢 · 04 🟢 · 05 🟡 (QA 100%, deploy pendiente).
- **Bloqueos:** deploy = plataformas de Kevin (repo en GitHub + Render + Vercel). *Verificación con LLM real completada (2026-11-13): matriz de verdad en verde (APROBADO / R3 / R4) y `PDF_SIN_TEXTO` sin créditos — requiere ADR-02-08 (fix Decimal del esquema strict) y ADR-02-09 (p95 > 8 s por outliers del proveedor). Falta solo la pasada visual de la UI con `EXTRACTOR_MODE=llm` (Kevin).*
- **Configuración del usuario (Kevin):** autonomía completa (tests, deps, archivos, commit local, LLM real, push/deploy) · verificación completa obligatoria · desvío menor → ADR y seguir; desvío de contrato/esquema/regla → preguntar · commits por fase.
- **Protocolo de sesión (misión implícita en AGENTS.md §3):** Kevin escribe una palabra y el agente ya sabe qué hacer — `arrancá` = módulo pendiente completo (anuncia y ejecuta, sin esperar confirmación) · `MOD-XX` / `MOD-XX Fase N` = override · `prueba` = solo próxima fase · `estado` = resumen · `todo` = continuo hasta el final · `DoD` = revisión final. Al cerrar un módulo: bitácora + estado 🟢 en specs/README.md + **esperar al usuario** (no continuar al siguiente módulo por su cuenta).

---

## Plantilla de entrada (copiar, completar y pegar al final)

```markdown
## [YYYY-MM-DD] Sesión — MOD-XX / Fase N

**Qué se hizo:**
- (tareas T-XX completadas, marcadas [x] en 03-tasks.md)

**Verificación ejecutada (evidencia real):**
- (ej.: pytest backend/tests/unit -v → 24 passed; npm run build → ok; ruff → sin hallazgos)

**Archivos creados/modificados clave:**
- (lista breve)

**Decisiones / ADRs nuevos (si los hay):**
- (desvíos registrados en 04-verification.md del módulo, con motivo)

**Estado exacto al cerrar:**
- (ej.: MOD-00 T-01..T-04 ✓; T-05..T-07 ✗ — frontend sin scaffold)

**Próximos pasos para la próxima sesión:**
1. (acción más urgente y concreta)
2. (…)

**Costo LLM real (si hubo llamadas en modo llm):**
- (ej.: 3 llamadas gpt-4o-mini, ~2.1k tokens entrada — USD ~0.001)
```

---

## Historial de sesiones

### [2026-11-12] Sesión 0 — Especificación SDD completa (v2)
**Qué se hizo:**
- Creadas las specs SDD completas: `specs/README.md` + 6 módulos × 4 archivos (25 documentos).
- Sesión de refinamiento con Kevin (15 preguntas): decisiones aplicadas y specs actualizadas.

**Decisiones firmes (registradas en ADRs de cada módulo):**
- Proveedor IA: OpenAI `gpt-4o-mini` (Structured Outputs, temp 0, 1 reintento).
- Solo facturas auditable: regla de admisión R0 (`REMITO_NO_AUDITABLE`) sin evaluar R1–R5.
- CUIT Módulo 11: dv=11→0, dv=10→9. Tolerancia R3 ±$1.00; tope R4 estricto >$500.000; R5 0–60 días con reloj `America/Argentina/Buenos_Aires`.
- PDFs ≤5 MB y ≤10 páginas; campos críticos faltantes → `EXTRACCION_FALLIDA`; `RECHAZADO` es `200 OK`.
- Latencia desglosada por etapa (`latencia_extraccion_ms`, `latencia_reglas_ms`, total).
- Deploy de cierre: Render + Vercel (SQLite efímero aceptado). Git: commit por módulo/fase.

**Estado exacto al cerrar:**
- Specs 100% listas y consistentes. Implementación 0%.

**Próximos pasos:**
1. `MOD-00` Fase 1: T-00 (git init + .gitignore + commit "specs SDD v1"), T-01 estructura de carpetas, T-02 venv + requirements.txt, T-03 config.py + .env.example, T-04 main.py + /health.
2. Continuar Fases 2–3 del MOD-00 (scaffold frontend + calidad base) y seguir el orden MOD-00→05.

### [2026-11-12] Sesión 1 — MOD-00 completo

**Qué se hizo:**
- T-00: `git init` + `.gitignore` + commit "specs SDD v1" (`c7caab5`).
- Fase 1 (T-01..T-04): estructura monorepo `backend/frontend/qa`; `requirements.txt` + venv (33 paquetes instalados sin errores); `backend/src/config.py` (pydantic-settings, 11 variables de DESIGN-00 §2) + `backend/.env.example`; `backend/src/main.py` app factory + CORS + `GET /api/v1/health`. Commit `6583ccc`.
- Fase 2 (T-05..T-07): scaffold Vite `react-ts` (Vite 8, React 19, TS 7) + Tailwind CSS v4 (`@tailwindcss/vite`) + `lucide-react`; 4 capas en `frontend/src/` con semillas (`domain/index.ts`, `application/index.ts`, `infrastructure/apiClient.ts`, `presentation/App.tsx`); proxy `/api` → `:8000` y `frontend/.env.example` con `VITE_API_URL`. Commit `df6cde5`.
- Fase 3 (T-08..T-10): `pyproject.toml` raíz (pytest `testpaths`/`pythonpath` + config ruff), `backend/tests/unit/test_smoke.py` (TestClient sobre `/health`), ruff en verde, `README.md` raíz con quickstart de 2 comandos y tablas de variables. Commit `147f8c2`.

**Verificación ejecutada (evidencia real):**
- `pip install -r requirements.txt` → sin errores (fastapi 0.162.5, pydantic 2.14.3, pypdf 7.0.1, ruff 0.17.4).
- `uvicorn src.main:app --port 8000` → `GET /api/v1/health` = `{"status":"ok","version":"0.1.0","extractor_mode":"mock"}`.
- CU-03: `EXTRACTOR_MODE=llm` en `.env` → health refleja `"llm"` sin tocar código (`.env` borrado tras la prueba).
- `npm run build` → `tsc -b && vite build` ✓ (2082 módulos, 2.09 s).
- `npm run dev` → `http://localhost:5173` responde 200 con title + `#root`.
- `pytest backend/tests/unit/test_smoke.py -v` → **1 passed** (ejecutado desde raíz y desde `backend/`).
- `ruff format --check` → 18 files already formatted · `ruff check backend` → All checks passed.

**Archivos creados/modificados clave:**
- Backend: `src/config.py`, `src/main.py`, `.env.example`, `requirements.txt`, `tests/unit/test_smoke.py`, estructura de capas con `__init__.py`.
- Frontend: `vite.config.ts`, `src/index.css`, `src/presentation/App.tsx`, `src/{domain,application,infrastructure}/*`, `.env.example`.
- Raíz: `pyproject.toml`, `README.md`, `.gitignore`.

**Decisiones / ADRs nuevos (si los hay):**
- Ninguno que cambie contratos de API, esquema de BD o reglas de negocio. Notas menores registradas aquí: (1) `create-vite v9` generó Vite 8.3.8 + React 19.3 + TypeScript 7.0.2 + oxlint como linter del scaffold (la calidad Python sigue a cargo de ruff, según spec); (2) `CORS_ORIGINS` se lee como string separado por comas y se expone como lista (`cors_origins_list`) — contrato idéntico a DESIGN-00 §2; (3) `.gitignore` extiende la lista de T-00 con `.env` (AGENTS.md §9: secretos nunca en el repo) y caches de pytest/ruff; (4) `App.tsx` vive en `frontend/src/presentation/` (espejo de capas) y `main.tsx` lo importa desde ahí.

**Estado exacto al cerrar:**
- MOD-00 **🟢 Completado** (T-00..T-10 ✓; checklist §2 y DoD §5 de `04-verification.md` íntegros en verde). MOD-01..MOD-05 ⚪ Pendientes.

**Próximos pasos para la próxima sesión:**
1. `arrancá` → **MOD-01** (motor de reglas R0–R5): leer los 4 docs de `specs/modules/01-motor-reglas/` y arrancar por la Fase 1 (modelos de dominio y VOs `CUIT`/`Monto` con `Decimal`).
2. Exigencias del módulo: cobertura `domain/` 100%, tests sin I/O, fechas fijas vía `ClockPort` (reloj `America/Argentina/Buenos_Aires`).

**Costo LLM real (si hubo llamadas en modo llm):**
- Sin llamadas LLM (solo se verificó el reflejo del modo vía `/health` con un `.env` temporal).

### [2026-11-12] Sesión 2 — MOD-01 completo (Dominio y Motor de Reglas)

**Qué se hizo:**
- Fase 1 (T-01..T-04): `domain/models.py` (ItemFactura, FacturaExtraida, ReglaResultado, ResultadoAuditoria.desde_reglas), VO `CUIT` (módulo 11, dv=11→0 / dv=10→9), puertos `PadronProveedoresPort` + `ClockPort`, `ContextoAuditoria` + `Protocol Regla` + helper `formato_ars`.
- Fase 2 (T-05..T-10): reglas R1–R5 con códigos de error exactos y mensajes es-AR; `engine.py` con admisión R0 (REMITO corta antes de R1–R5), evaluación completa sin cortocircuito y reglas inyectables.
- Fase 3 (T-11..T-13): `backend/data/proveedores.json` (3 activos + 1 inactivo), `JsonPadronProveedores` (cache, normalización de guiones, warning si falta el archivo), `RelojSistema` (zoneinfo `America/Argentina/Buenos_Aires`).
- Fase 4 (T-14..T-17): `test_cuit.py` (24 casos), `test_reglas.py` (matriz de borde R1–R5), `test_engine.py` (CU-01/02/06/07, filas 22–24, inyectables, rendimiento <10 ms con 20 ítems), conftest con factory `factura(**overrides)`. Gate `--cov-fail-under=100` en verde.

**Verificación ejecutada (evidencia real):**
- `pytest backend/tests/unit -v` → **50 passed** (0.9 s).
- `pytest tests/unit --cov=src/domain --cov-report=term-missing --cov-fail-under=100` (desde `backend/`) → **Total 100%** (181 stmts, 0 miss) · `Required test coverage of 100% reached`.
- `ruff check backend` → All checks passed · `ruff format --check backend` → 35 files already formatted.
- Prueba de humo de adaptadores: padrón resuelve activo/inactivo/ausente y `RelojSistema().hoy()` = 2026-11-12 (-03:00).
- Grep de pureza: `domain/` sin imports de `fastapi|sqlite3|pypdf|openai|anthropic`.

**Archivos creados/modificados clave:**
- `backend/src/domain/`: `models.py`, `value_objects/cuit.py`, `ports/{padron_port,clock_port}.py`, `rules/base.py`, `rules/r1..r5_*.py`, `rules/engine.py`.
- `backend/src/infrastructure/`: `padron/json_padron.py`, `clock.py`; `backend/data/proveedores.json`.
- `backend/tests/unit/`: `conftest.py`, `test_cuit.py`, `test_reglas.py`, `test_engine.py`.
- `backend/requirements.txt`: `tzdata>=2024.1 ; sys_platform == "win32"`; `.gitignore`: artefactos de coverage.

**Decisiones / ADRs nuevos (si los hay):**
- `tzdata` añadida con marcador win32 — **aprobado por Kevin** vía pregunta (zoneinfo no resuelve en Windows sin el paquete).
- 6 ADRs menores en `04-verification.md` §4: sintaxis `X | None`/`Sequence` (reglas UP de ruff), `Proveedor` en `ports/padron_port.py`, guard defensivo del DV, `detalles` tipado + `formato_ars` es-AR, factory en conftest. Ninguno cambia contratos de API, esquema de BD ni reglas de negocio.

**Estado exacto al cerrar:**
- MOD-01 **🟢 Completado** (T-01..T-17 ✓; matriz de 24 filas cubierta; DoD §5 íntegro). MOD-02..MOD-05 ⚪ Pendientes.

**Próximos pasos para la próxima sesión:**
1. `arrancá` → **MOD-02** (ingesta PDF + extracción IA): leer los 4 docs de `specs/modules/02-extraccion-ia/`; depende del dominio de este módulo (`FacturaExtraida`) y de `EXTRACTOR_MODE=mock` por default.
2. Ojo con límites ya implementados: PDF ≤ 5 MB, ≤ 10 páginas, `PDF_SIN_TEXTO` → 422, campos críticos faltantes → `EXTRACCION_FALLIDA` (502).

**Costo LLM real (si hubo llamadas en modo llm):**
- Sin llamadas LLM en esta sesión (todo el módulo es Python puro; el extractor IA recién entra en MOD-02).

### [2026-11-12] Sesión 3 — MOD-02 completo (Ingesta PDF y Extracción IA)

**Qué se hizo:**
- Fase 1 (T-01..T-02): puerto `PdfTextPort`; `PypdfTextExtractor` (concatena páginas, guarda defensivos `PdfInvalidoError`/`PdfDemasiadasPaginasError` >10 páginas/`PdfSinTextoError` <20 chars significativos); taxonomía de errores en `domain/errors.py` con atributo `codigo` (ADR-02-02).
- Fase 2 (T-03..T-05): `DocumentExtractorPort` + `ExtraccionResultado` en `models.py` (reutiliza `FacturaExtraida`); fixtures `extraccion-esperada.json` (CUIT 30-12345678-1, matemática consistente, fecha 2026-11-07 = hoy−5) y `extraccion-rechazado.json` (desvío $1.800 → R3); `MockExtractor` determinista (< 2 ms, ADR-02-06 fecha estática).
- Fase 3 (T-06..T-09): `client.py` (SDK openai con import perezoso, `response_format` json_schema strict, `temperature=0`, esquema adaptado vía `preparar_esquema_estricto` — ADR-02-03); `prompt.py` (SYSTEM_PROMPT literal + user truncado a 30.000 chars + refuerzo en reintento); `LLMStructuredExtractor` (intento+1 reintento sobre ValidationError, latencia loggeada, `json_crudo_ia` conservado); `factory.py` (mock/llm + error claro sin key). `openai>=1.40` agregada a requirements.txt e instalada (3.49.0) — **aprobado por Kevin**.
- Fase 4 (T-10..T-13): `backend/tests/unit/test_extractor.py` — 33 tests: pypdf (texto, límite 10/11 páginas, corrupto, cifrado, guards), mock (determinismo, variantes contra esquema, desvío > $1.00, < 10 ms), LLM falsificado (ok, reintento, falla definitiva, error proveedor sin reintento), client (strict, sin key, SDK ausente, error proveedor, no-JSON), esquema strict (claves no soportadas fuera, objetos cerrados, enum/format/null), factory (default mock, variante, llm±key).

**Verificación ejecutada (evidencia real):**
- `pytest tests/unit/test_extractor.py -v --cov=src/infrastructure/pdf --cov=src/infrastructure/llm --cov-fail-under=90` → **33 passed, cobertura 100%** (155 stmts, 0 miss).
- `pytest tests/unit -q` → **84 passed** (1.49 s, todo offline con SDK falsificado).
- `pytest tests/unit --cov=src/domain --cov-fail-under=100` → **100%** (gate de MOD-01 intacto).
- `ruff check backend` → All checks passed · `ruff format --check backend` → 45 files already formatted.
- Smokes manuales: PDF mínimo generado en memoria (texto extraído + `PDF_SIN_TEXTO` con código correcto), mock en 1.74 ms con `json_crudo_ia` poblado, flujo completo LLM-falso (esquema strict, temperature=0, reintento con prompt reforzado, `EXTRACCION_FALLIDA` tras 2 intentos).

**Archivos creados/modificados clave:**
- `backend/src/domain/`: `errors.py`, `ports/pdf_text_port.py`, `ports/document_extractor_port.py`, `models.py` (+`ExtraccionResultado`).
- `backend/src/infrastructure/pdf/`: `pypdf_adapter.py`. `backend/src/infrastructure/llm/`: `client.py`, `prompt.py`, `structured_extractor.py`, `mock_extractor.py`, `factory.py`.
- `backend/data/fixtures/`: `extraccion-esperada.json`, `extraccion-rechazado.json`.
- `backend/tests/unit/test_extractor.py`; `backend/requirements.txt` (+`openai>=1.40`); `backend/src/config.py` (+`mock_variant`) y `.env.example` (+`MOCK_VARIANT`).

**Decisiones / ADRs nuevos (si los hay):**
- 7 ADRs en `04-verification.md` §4 (ADR-02-01..07): `openai` en requirements (aprobado por Kevin), errores en `domain/errors.py`, transformación del esquema al modo strict, fallo de proveedor sin reintento, `MOCK_VARIANT` en config, fixture mock con fecha estática (riesgo de vencimiento ≈ 2027-01-06 → regenerar), import perezoso del SDK + umbral de caracteres significativos sin espacios. Ninguno cambia contrato API, esquema de BD ni reglas de negocio.

**Estado exacto al cerrar:**
- MOD-02 **🟢 Completado** (T-01..T-13 ✓; DoD §5: 4/5 en verde, 1 pendiente por diseño — verificación con `EXTRACTOR_MODE=llm` sobre los 3 PDFs de ejemplo que genera MOD-03 T-04). MOD-03..MOD-05 ⚪ Pendientes.

**Próximos pasos para la próxima sesión:**
1. `arrancá` → **MOD-03** (API REST + SQLite): leer los 4 docs de `specs/modules/03-api-sqlite/`; Fase 1 arranca con `AuditoriaRepositoryPort` + DDL.
2. En esa sesión, tras generar los PDFs de ejemplo (T-04), ejecutar la verificación manual pendiente de MOD-02 §2 con `EXTRACTOR_MODE=llm` (registrar costo en bitácora).
3. Cablear `crear_extractor()` y `PypdfTextExtractor` en `main.py`/use case (T-11 de MOD-03).

**Costo LLM real (si hubo llamadas en modo llm):**
- Sin llamadas LLM en esta sesión (todo probado con SDK falsificado; el modo `llm` recién se ejercita al tener los PDFs de ejemplo en MOD-03).

### [2026-11-12] Sesión 4 — MOD-03 completo (API REST y SQLite)
**Qué se hizo:**
- Fase 1 (T-01..T-04): puerto `AuditoriaRepositoryPort` + modelo `RegistroAuditoria` en dominio; `infrastructure/db/esquema.sql` (DDL + índice, aplicado al arranque con `PRAGMA journal_mode=WAL`); `SqliteAuditoriaRepository` (una conexión compartida `check_same_thread=False`, lock `threading`, `cerrar()`, mapeo fila↔modelo con JSON); `scripts/generar_ejemplos.py` con `reportlab` genera los 3 PDFs en `backend/data/ejemplos/` (fechas hoy−5/−20/−30, TZ Buenos Aires) — PDFs verificados con pypdf y commiteados.
- Fase 2 (T-05..T-10): `AuditarComprobanteUseCase` (inyección de 5 puertos, latencias por etapa con `perf_counter`, `ERROR_EXTRACCION` persistido antes de propagar 502); `presentation/dtos.py` (ReglaResultadoDTO, RegistroAuditoriaDTO, ResumenAuditoriaDTO; montos Decimal→número 2 dec); routers `auditar` (413/422 pre-use case), `ejemplos` (catálogo estático + `StreamingResponse`), `historial` (limit/offset con defaults 20/0, detalle 404 tipado); `presentation/errores.py` (handlers → cuerpo `{"error": {codigo, mensaje}}`).
- Fase 3 (T-11..T-13): wire-up en `main.py` (routers + tablas al arranque + factory del extractor; `app` construido perezosamente vía `__getattr__` para no crear la BD real al importar; lifespan cierra la conexión); `tests/integration/test_api_auditar.py` (12 tests: filas 1–7 y 11 de la matriz + REMITO R0 + extensión .pdf con MIME desconocido + ids únicos); `test_api_historial.py` (9 tests: filas 8–10 + offset + vacío + PDF faltante); conftest de integración con reloj fijo (2026-11-12), stubs de extractor y SQLite en `tmp_path`.

**Verificación ejecutada (evidencia real):**
- `pytest tests/integration -v` → **20 passed**; `pytest tests -q` → **104 passed** (0 warnings tras el cierre de conexiones).
- Gates de cobertura: `domain/` **100%**, `application/auditar_comprobante.py` **100%** (>90% requerido), `infrastructure/db/sqlite_repository.py` **100%** (>90% requerido), `presentation/` routers y dtos **100%**. TOTAL 99% (única excepción: `main.py.__getattr__`, verificado con uvicorn).
- `ruff check src scripts tests` → All checks passed · `ruff format --check` → 57 files already formatted.
- Smoke manual con uvicorn real + curl (DoD §5): `/health` ok; `/ejemplos` devuelve los 3 con `url_pdf`; `/ejemplos/{id}/pdf` sirve `application/pdf` (1701 bytes); `POST /auditar` con el ejemplo aprobado → `200 APROBADO` en **34 ms** con datos, 5 reglas verdes, `json_crudo_ia`, latencias `(0, 1, 34)` y `creado_en` UTC; `.txt` → `422 PDF_INVALIDO`; blob 6 MB → `413 ARCHIVO_MUY_GRANDE`; `/historial?limit=5` sin `json_crudo_ia`; `/historial/{id}` con JSON crudo; 404 tipados (`AUDITORIA_NO_ENCONTRADA`, `EJEMPLO_NO_ENCONTRADO`).

**Archivos creados/modificados clave:**
- `backend/src/domain/`: `models.py` (+`RegistroAuditoria`), `ports/auditoria_repository_port.py`.
- `backend/src/infrastructure/db/`: `esquema.sql`, `sqlite_repository.py`.
- `backend/src/application/auditar_comprobante.py`; `backend/src/presentation/`: `dtos.py`, `errores.py`, `routers/{auditar,ejemplos,historial}.py`; `backend/src/main.py` (wire-up + lifespan + `__getattr__`).
- `backend/scripts/generar_ejemplos.py`; `backend/data/ejemplos/*.pdf` (3 commiteados); `backend/requirements.txt` (+`reportlab>=4.0`); `.gitignore` (+`-shm`/`-wal`).
- `backend/tests/integration/`: `conftest.py`, `test_api_auditar.py`, `test_api_historial.py`; `backend/tests/unit/test_smoke.py` (aislado con SQLite temporal).

**Decisiones / ADRs nuevos (si los hay):**
- 7 ADRs en `04-verification.md` §4 (ADR-03-01..07): DTOs con `cuit_emisor`/`monto_total` planos, `app` perezosa por `__getattr__`, lock+cierre de la conexión SQLite, handlers de error con cuerpo §3 (no `HTTPException`/`detail`), R4 probado con extractor stub (mock no cubre ese caso), `reportlab` solo del script, montos de `datos_extraidos` como número. Ninguno cambia contrato API, esquema de BD ni reglas de negocio.

**Estado exacto al cerrar:**
- MOD-03 **🟢 Completado** (T-01..T-13 ✓; DoD §5: 6/6 ítems en verde). MOD-04..MOD-05 ⚪ Pendientes.

**Próximos pasos para la próxima sesión:**
1. `arrancá` → **MOD-04** (frontend Clean Architecture): leer los 4 docs de `specs/modules/04-frontend/`; arranca con pantalla dividida contra esta API ya terminada.
2. Si Kevin carga `backend/.env` con `LLM_API_KEY`: ejecutar la verificación pendiente de MOD-02 §2 con `EXTRACTOR_MODE=llm` sobre los 3 PDFs de ejemplo (registrar costo acá).

**Costo LLM real (si hubo llamadas en modo llm):**
- Sin llamadas LLM (no hay `backend/.env` con key en la máquina; el modo `llm` no se pudo ejecutar).

### [2026-11-12] Sesión 5 — MOD-04 completo (Frontend Clean Architecture)

**Qué se hizo:**
- Fase 1 (T-01..T-03): `domain/types.ts` — espejo del contrato real de MOD-03 (ResultadoAuditoria con `cuit_emisor`/`monto_total` planos, ReglaResultado con `detalles` y `R0`, ResumenAuditoria sin `json_crudo_ia`, Ejemplo con `url_pdf`, CuerpoError); `infrastructure/apiClient.ts` — base `VITE_API_URL` (vacía → proxy `/api/v1`), `ErrorApi` con normalización del cuerpo `{"error":{codigo,mensaje}}` + red caída, `validarPdf` client-side (formato + ≤ 5 MB), y las 6 funciones: `auditarArchivo`, `auditarEjemplo` (GET pdf → blob → File → POST, T-03), `listarEjemplos`, `obtenerPdfEjemplo`, `listarHistorial`, `obtenerAuditoria`.
- Fase 2 (T-04..T-06): `useEjemplos()` (catálogo al montar + recargar), `useAuditoria()` (máquina `idle|loading|resultado|error`, guarda `pdfUrl` — URL de ejemplo o blob URL con revocación al reemplazar/desmontar, `verDetalle()` para CU-04, conserva el resultado previo si luego hay error → CU-05), `useHistorial()` (paginado limit 20 + `refrescar()`/`avanzar`/`retroceder`).
- Fase 3 (T-07..T-14): `App.tsx` pantalla dividida (`lg:grid-cols-[2fr_3fr]`, se apila < 1024px) con estados visual (empty-state, skeleton "Auditando documento…", resultado, BannerError encima sin perder pantalla); `BarraSuperior` (3 botones de ejemplo con chip del resultado esperado + tooltip descripción, Subir PDF con input oculto `accept="application/pdf"`, spinner y deshabilitados durante auditoría); `VisorPDF` (iframe + fallback de embed + "abrir en otra pestaña"); `SemaforoReglas` (badge APROBADO/RECHAZADO/ERROR DE EXTRACCIÓN + desglose `IA/reglas/total` + id + filas por regla con `codigo_error` monospace rojo); `TablaDatos` (cabecera + ítems + total, `es-AR`); `JsonInspector` (plegable con `datos_extraidos` + `json_crudo_ia`, Copiar por sección); `Historial` (tabla plegable, estado con chip de color, latencia ms, paginación, fila seleccionada re-carga detalle); `BannerError` (codigo + mensaje, acción opcional).
- Fase 4 (T-15..T-16): `presentation/formato.ts` con `Intl` es-AR (montos ARS, cantidades, fechas por partes sin TZ, timestamps), aria-labels/tooltips/foco, build tsc strict + oxlint en verde, quickstart de `README.md` actualizado (pantalla operativa + `VITE_API_URL` para Vercel).

**Verificación ejecutada (evidencia real):**
- `npm run build` → `tsc -b && vite build` ✓ (2095 módulos, ~2 s). `npm run lint` (oxlint) → sin hallazgos (2 avisos `set-state-in-effect` de la Fase 2 corregidos moviendo los `setState` a handlers).
- Smoke full-stack real: `uvicorn :8000` (mock) + `npm run dev`; vía proxy :5173 → `/health` 200 mock; `GET /ejemplos` 200 (3 ejemplos, contrato exacto); flujo completo `auditarEjemplo` (curl: descarga PDF → multipart POST) → `200 APROBADO` 5 reglas verdes, latencias `(IA 0, reglas 4, total 57) ms`, id `aud_*`.
- Camino RECHAZADO con segundo backend `:8001` + `MOCK_VARIANT=rechazado` → `RECHAZADO`, R3 roja `DISCREPANCIA_CONTABLE` con montos comparados y 4 verdes. *Con la variante default todos los PDFs dan APROBADO (mock determinista, RN-2-05 — no es un bug del frontend).*
- Errores: `.txt` → `422 PDF_INVALIDO`; blob 6 MB → `413 ARCHIVO_MUY_GRANDE` (cuerpo `{"error":{codigo,mensaje}}` exacto). Historial: listado 200 sin `json_crudo_ia` con latencia ms, detalle 200 con JSON crudo, `404 AUDITORIA_NO_ENCONTRADA` tipado.
- Grep anti-lógica-duplicada: solo literales de render (chips/badges/tipos del contrato); sin tope $500.000, sin módulo 11, sin cálculos en el cliente.
- Regresión: `pytest tests -q` → **104 passed** (3.3 s).

**Archivos creados/modificados clave:**
- `frontend/src/domain/`: `types.ts` (nuevo), `index.ts` (re-export). `frontend/src/infrastructure/apiClient.ts` (reescrito).
- `frontend/src/application/`: `useEjemplos.ts`, `useAuditoria.ts`, `useHistorial.ts`, `index.ts`.
- `frontend/src/presentation/`: `App.tsx` (reescrito), `formato.ts`, `components/{BarraSuperior,VisorPDF,SemaforoReglas,TablaDatos,JsonInspector,Historial,BannerError}.tsx`.
- `README.md` (quickstart + lint), `specs/modules/04-frontend/{03-tasks,04-verification}.md`, `specs/README.md` (estado MOD-04).

**Decisiones / ADRs nuevos (si los hay):**
- 3 ADRs en `04-verification.md` §4 (ADR-04-05..07): espejo de tipos alineado al contrato real de la API (el design §2 era boceto: `url_pdf`, planos, `detalles`, `R0`, `resultado_esperado: string`), default de base vía proxy `/api/v1` cuando `VITE_API_URL` está vacía, y **diferimiento de la pasada visual del checklist §2 a MOD-05** (Playwright automatiza esos 10 escenarios; en esta sesión se verificaron a nivel API/contrato con HTTP real). Ninguno cambia contrato API, esquema de BD ni reglas de negocio.

**Estado exacto al cerrar:**
- MOD-04 **🟢 Completado** (T-01..T-16 ✓; DoD §5: 3/5 en verde + 2 pendientes solo de pasada visual documentados con ADR-04-07). MOD-05 ⚪ Pendiente.

**Próximos pasos para la próxima sesión:**
1. **(2 min, Kevin)** Pasada visual de la checklist §2 con backend mock + frontend dev (`arrancá` backend y frontend): empty-state, 3 ejemplos, PDF en el visor, semáforo con latencias, JSON + Copiar, historial, banner 413/422, spinner. Marcar los 10 ítems y los 2 pendientes del DoD §5.
2. `arrancá` → **MOD-05** (QA): leer los 4 docs de `specs/modules/05-qa-testing/`; arranca por Playwright en `qa/e2e/auditoria.spec.ts` (automatiza exactamente la checklist de MOD-04) y k6 en `qa/load/`.
3. Si Kevin carga `backend/.env` con `LLM_API_KEY`: verificaciones con `EXTRACTOR_MODE=llm` pendientes (MOD-02 §2 + ejemplo R4 de la UI) y registrar costo.

**Costo LLM real (si hubo llamadas en modo llm):**
- Sin llamadas LLM (el frontend corre contra mock; sigue pendiente la key para el modo `llm`).

### [2026-11-12] Sesión 6 — MOD-05 Fases 1–4 completas (QA) + Fase 5 preparada

**Qué se hizo:**
- Fase 1 (T-01..T-04): verificación de suites (`unit/` + `integration/` ya organizadas) y del gate de cobertura oficial (`--cov-fail-under=95`); `test_smoke.py` ahora cierra su conexión SQLite (sin ResourceWarning).
- Fase 2 (T-05..T-07): Playwright 1.65 en la raíz (`package.json` + `playwright.config.ts` con `webServer` que levanta backend mock con BD efímera + frontend Vite, `retries: 0`), `qa/e2e/auditoria.spec.ts` con los 4 escenarios obligatorios, `qa/e2e/reset-db.mjs` y `qa/README.md`. Tres pasadas consecutivas en verde + capturas de la demo con `CAPTURAS=1` (en `docs/capturas/`). Requirió ADR-05-01: el `MockExtractor` resuelve la fixture por identidad del ejemplo (nombre `ej-…` o el PDF original re-subido) y se agregó la fixture `extraccion-monto-alto-sin-oc.json` — sin esto los escenarios R3/R4 del E2E eran imposibles en modo mock. Tests del mock ampliados (37 passed, cobertura de `infrastructure/llm` 100%).
- Fase 3 (T-08..T-10): `qa/load/stress_test.js` (rampa 30 s a 50 VUs, meseta 1 min, drenaje 15 s + `SMOKE=1` para CI) y corrida real contra backend mock con BD efímera; resultados registrados en `04-verification.md` §3.
- Fase 4 (T-11..T-13): `.github/workflows/verificacion.yml` (pytest gate → ruff → build frontend → Playwright → k6 smoke, con reporte E2E como artefacto; webServer hecho cross-platform), ADR-05-01..06, DoD §5 parcialmente marcado (7/10), `specs/README.md` (MOD-05 → 🟡) y `README.md` raíz con sección Calidad (umbrales reales) + capturas.
- Fase 4-bis (extensión del E2E): escenario 5 de subida propia — empty-state, `.txt` → `PDF_INVALIDO`, PDF 6 MB → `ARCHIVO_MUY_GRANDE`, ambos **sin perder el empty-state** (CU-05, validación client-side sin red), y flujo completo con un PDF real (`APROBADO`, visor con `iframe[src^="blob:"]`, estado "Auditando…" asertado amplificando la latencia del POST con `page.route` — ADR-05-07). Con esto quedó **cerrado el checklist §2 de MOD-04** (10/10) y su DoD §5 (5/5, ADR-04-07).
- Fase 5 (T-14..T-16) **preparada, no ejecutada**: `docs/despliegue.md` (guía Render + Vercel paso a paso, smoke post-deploy y notas operativas) + `render.yaml` (Blueprint). Requiere plataformas de Kevin (AGENTS.md §5: deploy solo con orden/configuración explícita).

**Verificación ejecutada (evidencia real):**
- `pytest backend/tests -q --cov=src --cov-fail-under=95` → **104 passed en 5.47 s**; dominio 100%, aplicación 100%, total 99.30%.
- Playwright: **4/4 passed en 24.3 s, 18.7 s y 19.4 s** (3 pasadas consecutivas, `retries: 0`, cero flakes); reporte HTML en `qa/artifacts/` (gitignored). Con el escenario 5: **5/5 passed en 33.5 s y 31.3 s** (2 pasadas consecutivas más, sin flakes).
- k6 completo: **0.00% errores (0/17.322 requests), p95 449.35 ms (< 500 ms), p50 239.08 ms, 5.774 iteraciones (54.98/s), 23.096/23.096 checks OK, 50 VUs en meseta**.
- k6 smoke (`SMOKE=1`, 10 VUs × 30 s): **0.00% errores, p95 71.93 ms, 1.521 iteraciones**.
- `ruff check backend` → All checks passed · `ruff format --check backend` → 57 files already formatted.
- Capturas E2E generadas y verificadas visualmente (3 PNG en `docs/capturas/`).

**Archivos creados/modificados clave:**
- Raíz: `package.json` + `package-lock.json` (@playwright/test), `playwright.config.ts`, `render.yaml`, `docs/despliegue.md`, `.github/workflows/verificacion.yml`, `README.md` (Calidad + capturas), `.gitignore` (+`test-results/`).
- `qa/`: `e2e/auditoria.spec.ts`, `e2e/reset-db.mjs`, `load/stress_test.js`, `README.md` (guía E2E + k6).
- Backend: `src/infrastructure/llm/mock_extractor.py` (routing por identidad de ejemplo + 3ª variante), `data/fixtures/extraccion-monto-alto-sin-oc.json` (nuevo), `src/config.py` y `.env.example` (comentarios), `tests/unit/test_extractor.py` (+3 tests).
- Docs: `docs/capturas/demo-0{1,2,3}-*.png`, specs (tasks/verification de MOD-05, verification de MOD-04 — checklist §2 y DoD cerrados, estado en specs/README.md).

**Decisiones / ADRs nuevos (si los hay):**
- ADR-05-01: mock por identidad del ejemplo (necesario para RN-5-04 sin LLM_API_KEY; no cambia contrato API/BD/reglas). Fecha estática de la fixture nueva (2026-10-13): mismo riesgo de vencimiento que ADR-02-06.
- ADR-05-02: reset de BD efímera dentro del comando del `webServer` (Playwright arranca webServers antes del globalSetup → EPERM).
- ADR-05-03: el E2E no aserta sobre el visor (Chromium headless no renderiza PDFs inline).
- ADR-05-04: k6 contra BD efímera `qa/artifacts/` (RN-5-05).
- ADR-05-05: workflow único de verificación sin deploy automático (SPEC-05 §5).
- ADR-05-06 (observación): p95 449 ms a 50 VUs — cuello de botella en la conexión SQLite compartida con lock; aceptado para la PoC.
- ADR-05-07: el estado "Auditando…" del escenario 5 se aserta amplificando la latencia del `POST /auditar` con `page.route` (delay 800 ms, solo en el navegador del test; backend real intacto) — la auditoría mock responde en < 10 ms y sin `retries` (RN-5-06) no hay forma estable de asertarlo. También se documenta que el E2E aserta `iframe[src^="blob:"]` (RN-4-04) sin afirmar el render interno del PDF (ADR-05-03 se mantiene).

**Estado exacto al cerrar:**
- MOD-05: **T-01..T-13 ✓** (QA completo y verificado), **T-14..T-16 ✗** (deploy de cierre pendiente de plataformas/orden de Kevin). Módulos 00–04 🟢 (MOD-04 con DoD 5/5: checklist §2 cerrado por el E2E) · 05 🟡.

**Próximos pasos para la próxima sesión:**
1. Deploy de cierre (T-14..T-16) siguiendo `docs/despliegue.md`: push a GitHub → Render (Blueprint `render.yaml`) → Vercel con `VITE_API_URL` → `CORS_ORIGINS` → smoke post-deploy → marcar T-14..T-16, DoD §5 completo y MOD-05 🟢 en `specs/README.md`.
2. Si Kevin carga `backend/.env` con `LLM_API_KEY`: verificaciones con `EXTRACTOR_MODE=llm` pendientes (MOD-02 §2 + ejemplo R4 en la UI) y registrar costo.
3. Opcional: `DoD` para la revisión final global (queda 1 ítem bloqueado solo por el deploy).

**Costo LLM real (si hubo llamadas en modo llm):**
- Sin llamadas LLM (todo el QA corre en modo mock, RN-5-01; el modo `llm` sigue pendiente de la key).

### [2026-11-13] Sesión 7 — Escenario real con LLM: `.env` a `llm`, fix de Decimal y matriz de verdad en verde

**Qué se hizo:**
- `backend/.env` (no versionado): `EXTRACTOR_MODE=mock → llm`. Kevin solo había agregado `LLM_API_KEY` (nombre correcto); faltaba ese cambio.
- Levantado full-stack en escenario real: backend `:8000` (venv, uvicorn) + frontend `:5173` (`npm.cmd run dev` — `npm` puro falla por ExecutionPolicy de PowerShell).
- **Bug encontrado en escenario real (ADR-02-08):** con LLM verdadero, el esquema strict admitía la rama string del `anyOf` que Pydantic genera para `Decimal` → el modelo devolvía montos es-AR (`'$200.000,00'`) → `ValidationError` en los 2 intentos → `502 EXTRACCION_FALLIDA` en los 3 ejemplos (el mock nunca lo mostraba porque devuelve números limpios).
  - Fix infraestructura: `preparar_esquema_estricto` colapsa `anyOf [{number},{string}]` a `{"type": "number"}` (opcional `string|null` intacto).
  - Refuerzo de prompt: montos siempre números JSON sin `$` ni separadores de miles; impuestos faltante = 0 (intento 1 y reintento).
  - Test de factory hecho determinista: `monkeypatch.setenv("EXTRACTOR_MODE","mock")` + `get_settings.cache_clear()` (antes dependía de que NO existiera `.env`; con el `.env` real en `llm` el test se rompía).
- Verificación real completada (MOD-02 §2, checkboxes y ADR-02-08/09 en `04-verification.md`): matriz de verdad `ej-factura-aprobada → APROBADO` / `ej-factura-desvio → RECHAZADO R3` / `ej-monto-alto-sin-oc → RECHAZADO R4`, 100% de campos extraídos correctos; PDF solo-gráficos (reportlab) → `422 PDF_SIN_TEXTO` sin consumir créditos; 10 extracciones reales: mediana 3.103 ms, outliers 10.4/10.8 s → p95 > umbral 8 s, desvío aceptado en ADR-02-09.
- Historial SQLite persistiendo auditorías reales (APROBADO/RECHAZADO con latencias ms y `ERROR_EXTRACCION` previos al fix por diseño).

**Verificación ejecutada (evidencia real):**
- `pytest tests -q --cov=src --cov-fail-under=95` → **109 passed**, cobertura total 99.59% (`infrastructure/llm` 100%).
- `ruff check backend` → All checks passed · `ruff format --check backend` → 57 files already formatted.
- Real `:8000` `/health` → `{"status":"ok","extractor_mode":"llm"}`; 3 auditorías reales con latencias IA 3.1/3.5/4.1 s (post-fix, primer intento); escaneado → `PDF_SIN_TEXTO` inmediato.
- Frontend `:5173` → HTTP 200 (proxy `/api/v1` contra el backend en modo `llm`).

**Archivos creados/modificados clave:**
- `backend/src/infrastructure/llm/client.py` (`_es_anyof_decimal` + colapso en `_limpiar`), `backend/src/infrastructure/llm/prompt.py` (SYSTEM_PROMPT + reintento reforzado), `backend/tests/unit/test_extractor.py` (+2 tests de esquema, factory determinista, import ordenado).
- Specs: `specs/modules/02-extraccion-ia/04-verification.md` (§2: 3 ítems cerrados; ADR-02-08 y ADR-02-09), `specs/PROGRESO.md` (esta entrada).
- Sin cambios de contrato API, esquema de BD ni reglas de negocio.

**Decisiones / ADRs nuevos (si los hay):**
- ADR-02-08 (Decimal → rama numérica en esquema strict, prompt reforzado, factory determinista en tests) y ADR-02-09 (p95 real > 8 s por outliers del proveedor; PoC acepta, umbral era de laboratorio). Ambos menores — sin contrato/esquema/reglas.

**Estado exacto al cerrar:**
- Módulos 00–04 🟢 · 05 🟡 (QA completo, deploy T-14..T-16 pendiente de plataformas de Kevin). Verificación con LLM real: **completada** (queda solo la pasada visual de la UI con `llm`, a cargo de Kevin — la app ya corre en ese modo).
- Servidores activos al cerrar: backend `:8000` (llm) + frontend `:5173`.

**Próximos pasos para la próxima sesión:**
1. (Kevin, 5 min) Pasada visual de la UI en `http://localhost:5173` con modo real: correr los 3 ejemplos (semáforo R3/R4 en rojo), ver JSON crudo, historial y latencias; confirmar ítem 3 de MOD-02 §2.
2. Deploy de cierre (T-14..T-16) con `docs/despliegue.md`: push a GitHub (lo ejecuta Kevin) → Render Blueprint (variables `EXTRACTOR_MODE=llm`, `LLM_API_KEY`, `CORS_ORIGINS`) → Vercel con `VITE_API_URL` → smoke post-deploy → DoD global (`DoD`).
3. En Render considerar el p95 real (~10.8 s): no rompe el flujo, pero documentar la latencia esperada del escenario real.

**Costo LLM real (si hubo llamadas en modo llm):**
- ~29 llamadas `gpt-4o-mini` (~2k tokens entrada + ~250 salida c/u): 16 en intentos fallidos pre-fix (auditorías que terminaron en 502), 1 de exploración, 12 en verificaciones post-fix (matriz × 2, escaneado no consumió, medición de latencia × 10) — **USD ≈ 0.015 (estimado)**. Ninguna auditoría desde el fix necesitó reintento.

### [2026-11-13] Sesión 8 — Extensión del E2E a 10 escenarios (solicitud de Kevin)

**Qué se hizo:**
- Kevin pidió ≥ 5 casos E2E nuevos; elegidos con pregunta (A+B+C+D+E): R0 remito, PDF_SIN_TEXTO, 11 páginas, red caída y EXTRACCION_FALLIDA.
- Backend (solo mock, ADR-05-08): fixture `extraccion-remito.json` (tipo REMITO, fecha estática — R0 corta antes de R5) + marca `"remito"` en `MARCAS_EJEMPLOS` del `MockExtractor`; test unitario del routing (pytest 110 passed, cobertura `infrastructure/llm` 100%).
- Fixtures E2E commiteadas en `qa/e2e/fixtures/`: `remito-transporte-2026.pdf` (1 pág. con texto), `pdf-escaneado-grafico.pdf` (0 chars de texto), `factura-11-paginas.pdf` (11 págs.) — generadas por el nuevo `backend/scripts/generar_fixtures_e2e.py` (reportlab) y verificadas con pypdf (chars/páginas correctos).
- E2E: escenarios 6–10 en `qa/e2e/auditoria.spec.ts` (describe "Escenarios extendidos"); 9 y 10 usan `page.route` (abort / fulfill 502) sin tocar el backend real, asertando CU-05 (resultado previo conservado).
- Docs: `qa/README.md` (10 escenarios + regeneración de fixtures), T-06-bis en `03-tasks.md`, checklist §2 + ADR-05-08 en `04-verification.md`.

**Verificación ejecutada (evidencia real):**
- `pytest tests -q` → **110 passed** · `ruff check backend` → All checks passed · `ruff format --check backend` → 58 files already formatted.
- Playwright **10/10 passed en 2 pasadas consecutivas** (1.3 m / 34.4 s), `retries: 0`, cero flakes (npx.cmd por ExecutionPolicy de PowerShell).
- **Fix post-reporte de Kevin (escenario 2 fallaba):** `reuseExistingServer` hacía que el E2E reutilizara el backend manual en modo `llm` → la matriz mock no aplicaba (montos $270.000/$285.000 vs $28.200/$30.000 de la fixture). Corregido con ADR-05-09: puertos exclusivos (backend :8010, frontend :5175), `reuseExistingServer: false` y proxy del frontend configurable por `VITE_PROXY_TARGET` (default :8000 intacto). Re-verificado: **10/10 × 2 pasadas (52 s / 35.1 s) con el backend manual llm corriendo en :8000 en paralelo**.

**Archivos creados/modificados clave:**
- Backend: `src/infrastructure/llm/mock_extractor.py` (variante + marca remito), `data/fixtures/extraccion-remito.json` (nuevo), `scripts/generar_fixtures_e2e.py` (nuevo), `tests/unit/test_extractor.py` (+1 test).
- QA: `qa/e2e/auditoria.spec.ts` (+5 escenarios, header actualizado), `qa/e2e/fixtures/*.pdf` (3 commiteados), `qa/README.md`.
- Specs: `03-tasks.md` (T-06-bis) y `04-verification.md` (§2 + ADR-05-08) de MOD-05; `specs/PROGRESO.md` (esta entrada).

**Decisiones / ADRs nuevos (si los hay):**
- ADR-05-08: extensión E2E a 10 escenarios + fixture REMITO del mock + PDFs fixture del E2E. Menor: sin cambios de contrato API, esquema de BD ni reglas de negocio (el caso R0 ya estaba probado a nivel dominio).
- ADR-05-09: puertos exclusivos del E2E (backend :8010, frontend :5175) + `reuseExistingServer: false` + `VITE_PROXY_TARGET` en `vite.config.ts`. Menor: es tooling de QA; el uso manual (:8000/:5173) no cambia. Motiva el bug del escenario 2 reportado por Kevin.

**Estado exacto al cerrar:**
- Módulos 00–04 🟢 · 05 🟡 (QA completo con E2E 10/10; deploy T-14..T-16 pendiente de plataformas de Kevin). Servidores levantados al cerrar: backend `:8000` (modo llm) + frontend `:5173`.

**Próximos pasos para la próxima sesión:**
1. Deploy de cierre (T-14..T-16) con `docs/despliegue.md`: push de `main` a GitHub (lo ejecuta Kevin) → Render Blueprint → Vercel (`VITE_API_URL`, `CORS_ORIGINS`) → smoke post-deploy → DoD global.
2. En Render, decidir `EXTRACTOR_MODE` de producción (llm real vs mock de demo) y registrar la key como variable de entorno de la plataforma (nunca en el repo).

**Costo LLM real (si hubo llamadas en modo llm):**
- Sin llamadas LLM en esta sesión (el E2E corre en modo mock, RN-5-01; los escenarios 9–10 interceptan la red a nivel navegador).

### [2026-11-13] Sesión 9 — k6 funcional: correctitud del contrato bajo carga (solicitud de Kevin)

**Qué se hizo:**
- Kevin pidió además pruebas k6 **funcionales** (no solo saturación); elegido con pregunta: grupos 1+2+3 — contrato de API + matriz de verdad + caminos de error, un solo script con escenarios elegibles por env y smoke corto para CI.
- `qa/load/funcional.js` (ADR-05-10): 3 escenarios con `check` de contenido — `contrato` (health en modo mock, catálogo con `resultado_esperado`, PDFs con magia `%PDF`, auditoría con id `aud_*` + latencias, historial sin `json_crudo_ia`, detalle con `json_crudo_ia`), `matriz` (3 ejemplos + remito fixture del E2E como fuente única: APROBADO 5 ✅ / solo-R3 / solo-R4 / R0 con 1 regla) y `errores` (422 `PDF_INVALIDO`, 413 `ARCHIVO_MUY_GRANDE`, 404 `AUDITORIA_NO_ENCONTRADA`, 404 `EJEMPLO_NO_ENCONTRADO`).
- Selección por env: `ESCENARIO=todo|contrato|matriz|errores` (inválido → error claro) y `SMOKE=1` para CI; umbrales `checks` > 99%, `http_req_failed` por escenario y p95 < 500 ms.
- Ajuste de diseño tras la 1ª corrida: a 14 VUs sin pausa satura el lock de la SQLite (p95 > 500 ms, EXIT=99) → **pausa de 1 s por iteración**: la saturación la mide `stress_test.js` (ADR-05-06), este script mide correctitud bajo concurrencia moderada.
- CI: stage nuevo en `.github/workflows/verificacion.yml` tras el k6 smoke (`SMOKE=1 k6 run qa/load/funcional.js`, reutiliza el backend mock ya levantado en el job).
- Docs: `qa/README.md` (árbol, comandos del k6 funcional, tabla de escenarios, umbrales, nota de diseño) + ADR-05-10 en `04-verification.md`.

**Verificación ejecutada (evidencia real):**
- Backend mock propio en `:8010` con BD efímera `qa/artifacts/k6-funcional.db` (RN-5-05; para no tocar la instancia `llm` de Kevin en `:8000`) — detenido al cerrar.
- k6 completo (~2 min): **EXIT=0**, 7008 requests, `http_req_failed` **0.00%** en `contrato` y `matriz` (10.5% global = 4xx esperados de `errores`), **p95 337 ms < 500 ms**, todos los checks OK.
- k6 smoke (`SMOKE=1`, ~30 s): **EXIT=0** · los 3 escenarios individuales (`ESCENARIO=…` + smoke): **EXIT=0** cada uno.
- `ESCENARIO=inexistente` → mensaje claro de escenarios válidos y **EXIT=107** (fail-fast antes de tocar la API).

**Archivos creados/modificados clave:**
- `qa/load/funcional.js` (nuevo), `.github/workflows/verificacion.yml` (+stage), `qa/README.md` (sección Funcional), `specs/modules/05-qa-testing/04-verification.md` (ADR-05-10), `specs/PROGRESO.md` (esta entrada).
- `package.json` + `package-lock.json`: `@types/node` (dev) — resto sin commitear de la Sesión 8 (el spec E2E usa `node:fs`/`node:path`/`process`/`Buffer`).

**Decisiones / ADRs nuevos (si los hay):**
- ADR-05-10: k6 funcional separado del test de saturación; fixture remito reutilizada del E2E (fuente única); threshold `http_req_failed` por escenario (los 4xx de `errores` son esperados); pausa 1 s por iteración. Menor: herramienta de QA, sin cambios de contrato API/esquema/reglas.

**Estado exacto al cerrar:**
- Módulos 00–04 🟢 · 05 🟡 (QA completo: E2E 10/10 + k6 saturación + k6 funcional; deploy T-14..T-16 pendiente de plataformas de Kevin). Rama `sumarTestPlaywrite` (4 commits delante de `main`; push lo ejecuta Kevin).

**Próximos pasos para la próxima sesión:**
1. Deploy de cierre (T-14..T-16) con `docs/despliegue.md`: push de las ramas a GitHub (lo ejecuta Kevin; el CI corre el nuevo stage de k6 funcional) → Render Blueprint → Vercel (`VITE_API_URL`, `CORS_ORIGINS`) → smoke post-deploy → DoD global.
2. En Render, decidir `EXTRACTOR_MODE` de producción (llm real vs mock de demo) y registrar la key como variable de entorno de la plataforma (nunca en el repo).

**Costo LLM real (si hubo llamadas en modo llm):**
- Sin llamadas LLM (k6 y E2E corren en modo mock, RN-5-01).

### [2026-11-13] Sesión 10 — Refresh de documentación + unificación de ramas (solicitud de Kevin)

**Qué se hizo:**
- Kevin pidió: (1) toda la documentación actualizada, (2) unir `sumarTestPlaywrite` a `main` con todo funcional, (3) el push lo ejecuta él.
- Refresh de docs: `README.md` raíz (sección Calidad: E2E 10 escenarios con puertos exclusivos 8010/5175, k6 saturación **y funcional**, tabla de umbrales con datos reales de esta sesión; tabla de variables frontend con `VITE_PROXY_TARGET` y nota del proxy de desarrollo), `specs/README.md` (nota de MOD-05: k6 funcional incluido), `docs/despliegue.md` (prerrequisito con el remote real `kvnn04/sofredoc` + smoke opcional del caso R0 con el remito fixture), `AGENTS.md` §10 (comando del k6 funcional + puertos del E2E).
- `specs/modules/05-qa-testing/03-tasks.md`: T-10-bis (k6 funcional) registrada y marcada `[x]`.
- Ya al día de sesiones previas: `qa/README.md` (ADR-05-10), `specs/PROGRESO.md`, `04-verification.md`. Intactos por decisión: `CLAUDE.md` (puntero a AGENTS.md), `frontend/README.md` (boilerplate de Vite), docs históricos (`SofreDoc-Validator-Especificacion.md`, `crear specs.md`).
- **Unificación:** merge **fast-forward** de `sumarTestPlaywrite` → `main` (k6 funcional + E2E 10 escenarios + fix de puertos + docs). Sin push (lo ejecuta Kevin).

**Verificación ejecutada (evidencia real):**
- `pytest backend/tests -q --cov=src --cov-fail-under=95` → **110 passed en 8.60 s**; cobertura total **99.59%**, dominio 100% (gate ok).
- `ruff check backend` → All checks passed · `ruff format --check backend` → 58 files already formatted.
- `npm run build` (frontend) → **built in 2.37 s**.
- E2E Playwright → **10/10 passed (1.0 m)**, `retries: 0`.
- Servidores de Kevin arriba e intactos: backend `:8000` (modo llm) + frontend `:5173`.

**Archivos creados/modificados clave:**
- `README.md`, `specs/README.md`, `docs/despliegue.md`, `AGENTS.md` (§10), `specs/modules/05-qa-testing/03-tasks.md` (T-10-bis), `specs/PROGRESO.md` (esta entrada).

**Decisiones / ADRs nuevos (si los hay):**
- Ninguno: solo actualización de documentación y operación de git (merge ff, sin cambios de contrato/esquema/reglas).

**Estado exacto al cerrar:**
- `main` == `sumarTestPlaywrite` (post-merge, historial lineal), árbol completo en verde. Módulos 00–04 🟢 · 05 🟡 (falta deploy T-14..T-16). Pendiente el push de `main` a GitHub (lo ejecuta Kevin).

**Próximos pasos para la próxima sesión:**
1. Push de `main` a GitHub (`git push -u origin main`; opcional `git push origin sumarTestPlaywrite` para dejar la rama en el remoto) — el CI `.github/workflows/verificacion.yml` corre con el stage nuevo de k6 funcional.
2. Deploy de cierre (T-14..T-16) siguiendo `docs/despliegue.md` → marcar T-14..T-16 + DoD §5 → MOD-05 a 🟢 en `specs/README.md` → revisión final global (`DoD`).

**Costo LLM real (si hubo llamadas en modo llm):**
- Sin llamadas LLM (verificación en modo mock, RN-5-01).

### [2026-11-13] Sesión 11 — Fix CI: instalación de k6 con suite apt `stable` (error en el primer run de GitHub Actions)

**Qué se hizo:**
- Kevin reporta el error del CI: `Err:8 https://dl.k6.io/deb ubuntu Release — 404 Not Found` en el step "Instalar k6" de `verificacion.yml` (runner ubuntu-latest = Ubuntu 26.04 "resolute").
- Diagnóstico: el workflow usaba la instrucción apt **vieja** de k6 (`... https://dl.k6.io/deb ubuntu main`); el repo de k6 ya no publica `dists/ubuntu` — hoy publica el suite **`stable`** (docs vigentes de Grafana, verificados vía HTTP: `https://dl.k6.io/deb/dists/stable/Release` con `Suite: stable`, `Components: main`, amd64). Nunca había corrido ese step: era el primer run de CI.
- Fix: `ubuntu main` → `stable main` en `k6.list` + `curl -fsSL` (como en los docs) + comentario explicativo en el workflow.

**Verificación ejecutada (evidencia real):**
- `GET https://dl.k6.io/deb/dists/stable/Release` → 200, Release file válida (`Suite: stable`, architectures amd64/i386).
- Re-run del CI por Kevin tras push (verificar que el job quede en verde completo: pytest → ruff → build → E2E → k6 smoke → k6 funcional).

**Archivos creados/modificados clave:**
- `.github/workflows/verificacion.yml` (step "Instalar k6"), `specs/PROGRESO.md` (esta entrada).

**Decisiones / ADRs nuevos (si los hay):**
- Ninguno: fix de tooling de CI (sin cambios de contrato API/esquema/reglas).

**Estado exacto al cerrar:**
- `main` en `71a8f90` + este fix commiteado localmente; pendiente push de Kevin y re-run del CI. Módulos 00–04 🟢 · 05 🟡 (falta deploy T-14..T-16).

**Próximos pasos para la próxima sesión:**
1. Push de `main` → CI en verde → deploy de cierre (T-14..T-16) con `docs/despliegue.md` → `DoD`.

**Costo LLM real (si hubo llamadas en modo llm):**
- Sin llamadas LLM.

### [2026-11-13] Sesión 12 — Fix CI: orden del historial no determinístico con mismo segundo (E2E escenario 4 falló en GitHub Actions)

**Qué se hizo:**
- Kevin reporta el 2º error de CI: escenario 4 del E2E falla al asertar `FALTA_ORDEN_COMPRA` (1 failed, 1 did not run por el `describe.serial`, 8 passed).
- Diagnóstico: `creado_en` persiste con precisión de **segundos** (`_ahora_utc` → `%Y-%m-%dT%H:%M:%SZ`) y el listado usaba `ORDER BY creado_en DESC` **sin desempate**. En el runner (rápido, ~1,3 s/test) las auditorías del escenario 2 y 3 cayeron en el mismo segundo → SQLite devolvió las filas empatadas en orden indefinido → la UI cargó como "más reciente" la del escenario 2 (RECHAZADO R3) y `FALTA_ORDEN_COMPRA` (R4) no aparecía. Local no fallaba por timing (~50 s de corrida, segundos distintos).
- Fix (ADR-03-08): `ORDER BY creado_en DESC, rowid DESC` en `SqliteAuditoriaRepository.listar` — `rowid` refleja el orden de inserción, así el "más nuevo primero" (CU-04) es determinístico incluso con segundo empatado. Sin cambios de DDL, contrato API ni reglas.
- Test nuevo `test_fila_8_mismo_segundo_desempate_por_insercion`: 3 filas con mismo `creado_en` → orden de inserción invertido (reproduce el bug de CI a nivel integración).

**Verificación ejecutada (evidencia real):**
- `pytest backend/tests -q --cov=src --cov-fail-under=95` → **111 passed** (corrida limpia 11.15 s); cobertura total **99.59%**, dominio 100% (gate ok).
- `ruff check backend` → All checks passed · `ruff format --check backend` → 58 files already formatted.
- E2E Playwright con el fix → **10/10 passed (54.5 s)**.

**Archivos creados/modificados clave:**
- `backend/src/infrastructure/db/sqlite_repository.py` (ORDER BY con desempate), `backend/tests/integration/test_api_historial.py` (+1 test), `specs/modules/03-api-sqlite/04-verification.md` (ADR-03-08), `specs/PROGRESO.md` (esta entrada).

**Decisiones / ADRs nuevos (si los hay):**
- ADR-03-08 (MOD-03): desempate por `rowid DESC`. Menor: refuerza el CU-04 sin cambiar DDL/contrato/reglas.

**Estado exacto al cerrar:**
- `main` con este fix commiteado localmente; pendiente push de Kevin y re-run del CI (que debería llegar verde hasta k6). Módulos 00–04 🟢 · 05 🟡 (falta deploy T-14..T-16).

**Próximos pasos para la próxima sesión:**
1. Push de `main` → CI en verde → deploy de cierre (T-14..T-16) con `docs/despliegue.md` → `DoD`.

**Costo LLM real (si hubo llamadas en modo llm):**
- Sin llamadas LLM (verificación en modo mock, RN-5-01).
