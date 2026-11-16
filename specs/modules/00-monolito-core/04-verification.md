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

> **Índice maestro:** todas las decisiones del proyecto —numeradas y de base— están catalogadas y enlazadas por tema en [`specs/ADRs.md`](../../ADRs.md). El texto completo vive en [`specs/adr/`](../../adr/): las decisiones de base de este módulo en el consolidado [`base-00-01-core-y-reglas.md`](../../adr/base-00-01-core-y-reglas.md). Esta sección queda como tabla resumen de navegación.

### Decisiones de base (sin ID)

Texto completo (motivo e impacto): [`base-00-01-core-y-reglas.md` · MOD-00](../../adr/base-00-01-core-y-reglas.md#mod-00-arquitectura-monolito-y-core)

| Fecha | Decisión |
| :--- | :--- |
| 2026-11-12 | Migrar de `backend/app/` plano a Clean Architecture `backend/src/` |
| 2026-11-12 | `pypdf` como parser PDF del MVP |
| 2026-11-12 | Sin ORM (`sqlite3` stdlib) |

## 5. Criterio de Aceptación Final (Definition of Done)

- [x] Todas las tareas de `03-tasks.md` están marcadas como `[x]`.
- [x] El suite smoke de Pytest pasa en verde.
- [x] Backend y frontend arrancan con los comandos del quickstart del `README.md`.
- [x] `/api/v1/health` refleja la configuración del `.env` sin cambios de código.
- [x] `npm run build` y `ruff check .` en verde.
