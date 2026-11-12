# PROGRESO.md — Bitácora de Continuidad del Proyecto

> **Para todo agente de IA:** este archivo es tu punto de partida junto con `AGENTS.md`. Describe el estado **exacto** del proyecto. Al cerrar tu sesión, agregá una entrada nueva al final usando la plantilla de abajo. No edites ni borres entradas anteriores (el historial es trazabilidad).

---

## Estado actual (resumen rápido)

- **Fase del proyecto:** Implementación iniciada — **MOD-00..MOD-04 completos** (core + reglas + extracción + API/SQLite + **frontend de pantalla dividida**, todo en verde).
- **Siguiente acción concreta:** `MOD-05` Fase 1 → QA (Pytest ya cubierto; Playwright e2e en `qa/e2e/` + k6 en `qa/load/` + deploy Render/Vercel) según `specs/modules/05-qa-testing/`.
- **Módulos:** 00 🟢 · 01 🟢 · 02 🟢 · 03 🟢 · 04 🟢 (checklist visual §2 pendiente de pasada de Kevin o de MOD-05 Playwright) · 05 ⚪ Pendiente.
- **Bloqueos:** ninguno para MOD-05. *Pendientes con LLM real (siguen de sesiones anteriores): verificación de MOD-02 §2 y del ejemplo R4 de la UI con `EXTRACTOR_MODE=llm` — falta `backend/.env` con `LLM_API_KEY`.*
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
