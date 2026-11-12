# VERIFICATION-00: Arquitectura Monolito & Core — Testing y Cierre

> **Audiencia:** QA, Lead Developer, CI/CD.

## 1. Pruebas Unitarias e Integración (Pytest)

```bash
# Smoke: import de la app y health check
pytest backend/tests/unit/test_smoke.py -v
```

### Cobertura Mínima Requerida
Para este módulo no aplica cobertura de dominio (no hay reglas aún); solo se exige que el suite smoke pase.

## 2. Verificación Manual (Zero-Setup)

- [x] `pip install -r backend/requirements.txt` completa sin errores (Python 3.11+).
- [x] `uvicorn src.main:app --reload --port 8000` arranca desde `backend/` y `GET http://localhost:8000/api/v1/health` responde `200` con `extractor_mode` correcto.
- [x] `npm install && npm run dev` arranca desde `frontend/` y `http://localhost:5173` renderiza sin errores de consola.
- [x] Copiar `.env.example` → `.env`, cambiar `EXTRACTOR_MODE=llm` y verificar que `/api/v1/health` refleja el cambio sin tocar código.
- [x] `npm run build` (tsc + vite build) termina en verde.
- [x] `ruff check .` en `backend/` sin hallazgos.

## 3. Pruebas de Estrés y Rendimiento (k6)

No aplica en este módulo (se ejecuta desde MOD-05 con la API completa).

## 4. Registro de Decisiones de Arquitectura (ADR Log)

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | Migrar de `backend/app/` plano a Clean Architecture `backend/src/` | La guía SDD exige separación de capas; el documento original era monolito plano de 5 archivos. | Mejor testabilidad; se documenta el mapeo en `specs/README.md`. |
| 2026-11-12 | `pypdf` como parser PDF del MVP | Liviano y suficiente para PDFs digitales estándar; `pdfplumber` queda como fallback documentado. | Menos dependencias; riesgo documentado en MOD-02. |
| 2026-11-12 | Sin ORM (`sqlite3` stdlib) | PoC con 1 tabla; mantener dependencias mínimas. | DDL manual en MOD-03. |

## 5. Criterio de Aceptación Final (Definition of Done)

- [x] Todas las tareas de `03-tasks.md` están marcadas como `[x]`.
- [x] El suite smoke de Pytest pasa en verde.
- [x] Backend y frontend arrancan con los comandos del quickstart del `README.md`.
- [x] `/api/v1/health` refleja la configuración del `.env` sin cambios de código.
- [x] `npm run build` y `ruff check .` en verde.
