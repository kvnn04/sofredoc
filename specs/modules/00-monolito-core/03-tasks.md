# TASKS-00: Arquitectura Monolito & Core — Plan de Ejecución

> **Instrucción para la IA:** Ejecutar las tareas en orden estricto de dependencias. Tras completar cada tarea, marcar la casilla con `[x]` y asegurar que las pruebas unitarias sigan pasando.

## Fase 1: Esqueleto Backend (Core)

- [x] **T-00:** Inicializar git en la raíz, crear `.gitignore` (`backend/data/sofredoc.db`, `node_modules/`, `.venv/`, `dist/`, `__pycache__/`, `qa/artifacts/`) y hacer el primer commit "specs SDD v1"; el proyecto avanza con **un commit por módulo/fase** (decisión 2026-11-12).
- [x] **T-01:** Crear estructura de carpetas del monorepo según `02-design.md` (backend/frontend/qa/specs).
- [x] **T-02:** Crear entorno virtual Python y `backend/requirements.txt` con las dependencias de `02-design.md` §4; `pip install -r requirements.txt` sin errores.
- [x] **T-03:** Implementar `backend/src/config.py` con `Settings` (pydantic-settings) y crear `.env.example` con todas las variables de la tabla §2 con valores default seguros (`EXTRACTOR_MODE=mock`, `LLM_API_KEY` sin valor).
- [x] **T-04:** Implementar `backend/src/main.py` con app factory, CORS y `GET /api/v1/health`; verificar manualmente que `uvicorn src.main:app --reload` arranca y responde.

## Fase 2: Scaffold Frontend

- [x] **T-05:** Generar proyecto Vite `react-ts` en `frontend/`, instalar y configurar Tailwind CSS v4 y `lucide-react`; `npm run dev` renderiza la página base.
- [x] **T-06:** Crear las 4 capas (`domain/`, `application/`, `infrastructure/`, `presentation/`) en `frontend/src/` con archivos semilla y limpiar el boilerplate de Vite.
- [x] **T-07:** Configurar proxy `/api` → `http://localhost:8000` en `vite.config.ts` y variable `VITE_API_URL` en `.env.example` del frontend.

## Fase 3: Calidad Base

- [ ] **T-08:** Configurar `pytest` (raíz `pyproject.toml` o `pytest.ini`) con `testpaths = backend/tests` y crear `backend/tests/unit/test_smoke.py` que importe la app y haga ping a `/api/v1/health` (TestClient) — debe pasar.
- [ ] **T-09:** Configurar `ruff` (lint + format) y dejar el código existente en verde.
- [ ] **T-10:** Redactar el `README.md` raíz con quickstart de 2 comandos (backend + frontend) y tabla de variables de entorno.
