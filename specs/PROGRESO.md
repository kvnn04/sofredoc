# PROGRESO.md — Bitácora de Continuidad del Proyecto

> **Para todo agente de IA:** este archivo es tu punto de partida junto con `AGENTS.md`. Describe el estado **exacto** del proyecto. Al cerrar tu sesión, agregá una entrada nueva al final usando la plantilla de abajo. No edites ni borres entradas anteriores (el historial es trazabilidad).

---

## Estado actual (resumen rápido)

- **Fase del proyecto:** Implementación iniciada — **MOD-00 completo** (esqueleto monorepo + calidad base en verde).
- **Siguiente acción concreta:** `MOD-01` Fase 1 → dominio puro (modelos, VOs CUIT/Monto con `Decimal`) según `specs/modules/01-motor-reglas/`.
- **Módulos:** 00 🟢 Completado · 01 ⚪ Pendiente · 02 ⚪ Pendiente · 03 ⚪ Pendiente · 04 ⚪ Pendiente · 05 ⚪ Pendiente.
- **Bloqueos:** ninguno.
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
