# SofreDoc Validator

Aplicación web **IDP** (Intelligent Document Processing) que audita facturas en PDF: un LLM extrae los datos (Structured Outputs) y un **motor de reglas determinista** (R0–R5) decide el semáforo ✅/❌. PoC fullstack de Sofre Digital S.A.

- **Backend:** Python 3.11+ · FastAPI · Pydantic v2 · SQLite (stdlib) — Clean Architecture
- **Frontend:** React 19 · TypeScript · Vite · Tailwind CSS v4
- **Fuente de verdad:** [`specs/`](./specs/README.md) (SDD) · estado del proyecto en [`specs/PROGRESO.md`](./specs/PROGRESO.md)

## Decisiones clave en 60 segundos

| Decisión | Por qué | Evidencia |
| :--- | :--- | :--- |
| **La IA solo extrae; el sistema decide.** El LLM (Structured Outputs, `temperature=0`) convierte el PDF en un objeto Pydantic tipado; el semáforo ✅/❌ lo decide un motor determinista R0–R5 en Python puro con `Decimal` exacto. | Separar lo probabilístico de lo determinista: los datos extraídos nunca se "corrigen" y un `RECHAZADO` es resultado de negocio (200 OK), no error HTTP. | [`domain/rules/`](./backend/src/domain/rules/) · ADR-02-04 |
| **El LLM no suma:** `impuestos` se calcula en Python desde `detalle_impuestos` (líneas del pie extraídas una por una), con un gate de consistencia pre-reintento que reutiliza la misma ecuación de R3. | Pedirle la suma al modelo produjo un bug real ($94.600 por $145.800): la aritmética mental de un LLM no es fuente confiable para el control contable. | [ADR-02-12](./specs/modules/02-extraccion-ia/04-verification.md) · [`r3_matematica.py`](./backend/src/domain/rules/r3_matematica.py) |
| **3 falsos positivos resueltos con facturas AFIP reales:** Factura A con IVA discriminado, Factura B con Transparencia Fiscal (Ley 27.743) y Factura A mixta con percepciones. Cada fix fue semántico (schema + prompt), con R3 intacta y fixture de regresión. | La extracción falla en las reglas fiscales que un humano asume obvias; se corrigió iterando con LLM real (costo por tramo loggeado en la bitácora) sin tocar las reglas de negocio. | [ADR-02-10/11/12](./specs/modules/02-extraccion-ia/04-verification.md) |
| **QA en dos planos + CI:** 129 tests con gate de cobertura (dominio 100%), E2E Playwright con `retries: 0` (no oculta flakes), k6 de saturación **y** funcional (correctitud del contrato bajo carga). | Un test que falla al azar vale menos que ninguno; y "responde 200" no implica "responde el contrato correcto". | [`qa/README.md`](./qa/README.md) · [CI](./.github/workflows/verificacion.yml) |
| **Limitaciones conocidas y documentadas:** SQLite efímero en Render (el historial se reinicia por deploy), sin autenticación (PoC de alcance cerrado), lock de SQLite como cuello a 50 VUs (p95 462 ms), cold start del free tier. | Un PoC honesto declara sus bordes: cada limitación tiene su ADR y su camino de migración (el repositorio ya vive detrás de un puerto). | [ADR-05-06](./specs/modules/05-qa-testing/04-verification.md) · [`docs/despliegue.md`](./docs/despliegue.md) |

**Cómo se construyó:** metodología Spec-Driven ([`specs/`](./specs/README.md): 6 módulos × 4 documentos) con implementación orquestada por agentes de IA bajo reglas estrictas — arquitectura, decisiones y verificación del autor; ejecución asistida. Cada desvío quedó registrado como ADR y cada sesión con evidencia real en la bitácora: [`specs/PROGRESO.md`](./specs/PROGRESO.md) · protocolo de trabajo: [`AGENTS.md`](./AGENTS.md).

**Si sos técnico y tenés 5 minutos:** [`models.py`](./backend/src/domain/models.py) (el contrato con semántica AFIP), [`structured_extractor.py`](./backend/src/infrastructure/llm/structured_extractor.py) (el gate de consistencia) y [`sqlite_repository.py`](./backend/src/infrastructure/db/sqlite_repository.py), más los ADRs 02-08 (Decimal en strict), 02-12 (impuestos derivado) y 03-08 (bug real de concurrencia/timing en CI).

## Producción (demo en vivo) — desde 2026-11-15

- **App:** https://sofredoc.vercel.app (Vercel) · **API:** https://sofredoc-api.onrender.com (Render) — health: `GET /api/v1/health`
- Modo actual: `EXTRACTOR_MODE=mock` (determinista, sin costo de IA). Para evaluar con extracción real: en Render, `EXTRACTOR_MODE=llm` + `LLM_API_KEY` — verificado funcionando en producción.
- **SQLite efímero (free tier):** el historial arranca vacío tras cada deploy de Render (documentado y aceptado).
- **Cold start:** tras ~15 min sin tráfico, el primer request tarda ~30–60 s (el servicio se "despierta").
- Guía completa del deploy: [`docs/despliegue.md`](./docs/despliegue.md).

## Quickstart (2 comandos por terminal)

### 1. Backend — `http://localhost:8000`

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
uvicorn src.main:app --reload --port 8000
```

Salud del servicio: `GET http://localhost:8000/api/v1/health` → `{"status":"ok","version":"0.1.0","extractor_mode":"mock"}`

### 2. Frontend — `http://localhost:5173`

```powershell
cd frontend
npm install
npm run dev
```

El proxy de desarrollo redirige `/api` → `http://localhost:8000` (objetivo configurable con
`VITE_PROXY_TARGET`; útil para apuntar a otro backend, ej. el del E2E en `:8010`).

La pantalla dividida (MOD-04) es operativa: 3 ejemplos de 1 click + subida de PDF (≤ 5 MB) a la
izquierda el visor y a la derecha el semáforo R0–R5, los datos extraídos, el inspector de JSON
y el panel plegable de historial. Para desplegar el frontend (Vercel), definir
`VITE_API_URL=https://<backend>/api/v1`.

## Variables de entorno

Copiar `backend/.env.example` → `backend/.env` y `frontend/.env.example` → `frontend/.env` para personalizar. Los `.env` reales no se versionan.

| Variable (backend) | Default | Uso |
| :--- | :--- | :--- |
| `APP_ENV` | `dev` | Etiqueta de entorno/logging |
| `API_PORT` | `8000` | Puerto de uvicorn |
| `CORS_ORIGINS` | `http://localhost:5173` | Orígenes permitidos (separados por coma) |
| `DB_PATH` | `backend/data/sofredoc.db` | Archivo SQLite |
| `EXTRACTOR_MODE` | `mock` | `mock` \| `llm` (el modo `llm` requiere `LLM_API_KEY`) |
| `LLM_PROVIDER` | `openai` | Proveedor de extracción IA |
| `LLM_MODEL` | `gpt-4o-mini` | Modelo con Structured Outputs |
| `LLM_API_KEY` | *(vacía)* | Requerida solo si `EXTRACTOR_MODE=llm` |
| `PADRON_PATH` | `backend/data/proveedores.json` | Padrón de proveedores (R2) |
| `MAX_PDF_MB` | `5` | Tope de tamaño de subida |
| `TZ` | `America/Argentina/Buenos_Aires` | Zona horaria del reloj de negocio (R5) |

| Variable (frontend) | Default | Uso |
| :--- | :--- | :--- |
| `VITE_API_URL` | *(vacío → proxy `/api` de Vite)* | URL base de la API (producción, ej. Vercel → Render) |
| `VITE_PROXY_TARGET` | `http://localhost:8000` | Objetivo del proxy `/api` en desarrollo (ADR-05-09) |

## Calidad

```powershell
# Tests + gate de cobertura (desde la raíz; dominio 100%, total ≥ 95%)
backend\.venv\Scripts\python.exe -m pytest backend\tests -q --cov=src --cov-report=term-missing --cov-fail-under=95

# Lint + format (Python)
backend\.venv\Scripts\python.exe -m ruff check backend
backend\.venv\Scripts\python.exe -m ruff format backend

# Lint + build de producción (frontend)
cd frontend ; npm run lint ; npm run build

# E2E Playwright (levanta backend mock :8010 + frontend :5175 propios; 10 escenarios, retries 0)
npx playwright test qa/e2e/auditoria.spec.ts

# k6 saturación: rampa a 50 VUs (RN-5-01: SOLO con EXTRACTOR_MODE=mock)
k6 run qa/load/stress_test.js          # completa (~105 s)
$env:SMOKE="1" ; k6 run qa/load/stress_test.js   # smoke CI: 10 VUs × 30 s

# k6 funcional: contrato + matriz de verdad + errores bajo carga (pausa 1 s)
k6 run qa/load/funcional.js            # completa (~2 min)
$env:SMOKE="1" ; k6 run qa/load/funcional.js     # smoke CI (~30 s)
$env:ESCENARIO="matriz" ; k6 run qa/load/funcional.js ; $env:ESCENARIO=$null
```

Umbrales verificados (SLOs, detalle en `specs/modules/05-qa-testing/04-verification.md`):

| Métrica | Umbral | Obtenido |
| :--- | :--- | :--- |
| Tests Pytest (129) | < 30 s | **8.29 s** |
| Cobertura dominio / aplicación | 100% / > 90% | **100% / 100%** (total 99.61%) |
| E2E Playwright (10 escenarios) | 2 pasadas sin flakes | **10/10 passed × 2 pasadas** (última: 1.0 m) |
| k6 a 50 VUs: tasa de error | < 1% | **0.00%** |
| k6 a 50 VUs: latencia p95 | < 500 ms | **449.35 ms** |
| k6 funcional: checks de contenido | > 99% | **100%** (7008 requests, EXIT=0) |
| k6 funcional: latencia p95 | < 500 ms | **337.45 ms** |

Ver [qa/README.md](./qa/README.md) para la guía completa de QA.

## Capturas de la demo

Capturas reales generadas por la suite E2E (`CAPTURAS=1`, ver `qa/README.md`):

![Demo APROBADO](docs/capturas/demo-01-aprobado.png)
*Ejemplo #001: semáforo verde R1–R5 con desglose de latencia (IA / reglas / total), datos extraídos e inspector de JSON.*

![Demo RECHAZADO](docs/capturas/demo-02-rechazado.png)
*Ejemplo con desvío de monto: `RECHAZADO` por R3 (`DISCREPANCIA_CONTABLE`), el resto del semáforo en verde.*

![Demo JSON + historial](docs/capturas/demo-03-json-historial.png)
*Inspector de JSON (objeto Pydantic + crudo IA, copiable) e historial con estado y latencias por auditoría.*

## Estructura

```text
backend/    # FastAPI monolito (Clean Architecture: domain / application / infrastructure / presentation)
frontend/   # React + Vite (espejo de capas: domain / application / infrastructure / presentation)
qa/         # Playwright e2e + k6 load (MOD-05)
specs/      # Especificaciones SDD (fuente de verdad)
```
