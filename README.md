# SofreDoc Validator

Aplicación web **IDP** (Intelligent Document Processing) que audita facturas en PDF: un LLM extrae los datos (Structured Outputs) y un **motor de reglas determinista** (R0–R5) decide el semáforo ✅/❌. PoC fullstack de Sofre Digital S.A.

- **Backend:** Python 3.11+ · FastAPI · Pydantic v2 · SQLite (stdlib) — Clean Architecture
- **Frontend:** React 19 · TypeScript · Vite · Tailwind CSS v4
- **Fuente de verdad:** [`specs/`](./specs/README.md) (SDD) · estado del proyecto en [`specs/PROGRESO.md`](./specs/PROGRESO.md)

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

El proxy de desarrollo redirige `/api` → `http://localhost:8000` (configurable con `VITE_API_URL`).

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
| `VITE_API_URL` | *(vacío → proxy `/api` de Vite)* | URL base de la API |

## Calidad

```powershell
# Tests (desde la raíz)
backend\.venv\Scripts\python.exe -m pytest backend\tests -v

# Lint + format (Python)
backend\.venv\Scripts\python.exe -m ruff check backend
backend\.venv\Scripts\python.exe -m ruff format backend

# Build de producción (frontend)
cd frontend ; npm run build
```

## Estructura

```text
backend/    # FastAPI monolito (Clean Architecture: domain / application / infrastructure / presentation)
frontend/   # React + Vite (espejo de capas: domain / application / infrastructure / presentation)
qa/         # Playwright e2e + k6 load (MOD-05)
specs/      # Especificaciones SDD (fuente de verdad)
```
