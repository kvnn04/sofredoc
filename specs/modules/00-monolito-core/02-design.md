# DESIGN-00: Arquitectura Monolito & Core — Diseño Técnico

> **Audiencia:** Ingenieros de Software, Agentes de IA.
> **Patrón:** Clean Architecture (Monolito FastAPI + React).

## 1. Arquitectura de Componentes y Capas

```text
sofredoc-validator/
├── backend/
│   ├── src/
│   │   ├── domain/            # Entidades puras, Value Objects, Interfaces de Puertos
│   │   │   ├── models.py      # FacturaExtraida, ItemFactura, ReglaResultado, ...
│   │   │   ├── value_objects/ # CUIT, Monto
│   │   │   ├── rules/         # R1..R5 (MOD-01)
│   │   │   └── ports/         # DocumentExtractorPort, AuditoriaRepositoryPort, ...
│   │   ├── application/       # Casos de uso (Use Cases / Services)
│   │   │   └── auditar_comprobante.py
│   │   ├── infrastructure/    # Adaptadores (SQLite, PDF Parser, LLM Client, Padrón)
│   │   │   ├── db/            # SQLite (MOD-03)
│   │   │   ├── pdf/           # pypdf (MOD-02)
│   │   │   ├── llm/           # Structured Outputs + mock (MOD-02)
│   │   │   └── padron/        # proveedores.json (MOD-01)
│   │   ├── presentation/      # Endpoints FastAPI, DTOs de Request/Response
│   │   │   └── routers/
│   │   ├── config.py          # Settings (pydantic-settings)
│   │   └── main.py            # App factory + CORS + health
│   ├── tests/
│   │   ├── unit/
│   │   └── integration/
│   ├── data/
│   │   ├── proveedores.json   # Padrón simulado
│   │   ├── ejemplos/          # 3 PDFs de demostración
│   │   └── sofredoc.db        # SQLite (runtime, gitignored)
│   ├── scripts/
│   │   └── generar_ejemplos.py
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── domain/            # Modelos e Interfaces TS (tipos del contrato API)
│       ├── application/       # Hooks de orquestación (useAuditoria, useHistorial)
│       ├── infrastructure/    # Cliente API (fetch)
│       └── presentation/      # Componentes React + Tailwind
├── qa/
│   ├── e2e/                   # Playwright (MOD-05)
│   └── load/                  # k6 (MOD-05)
├── specs/                     # Este sistema de especificaciones
└── README.md
```

**Mapeo desde la estructura plana original** (ver `specs/README.md` § Mapa de Correspondencia): `main.py` → app factory + `presentation/routers/`; `schemas.py` → `domain/models.py`; `rules_engine.py` → `domain/rules/`; `extractor.py` → `infrastructure/pdf/` + `infrastructure/llm/`; `database.py` → `infrastructure/db/`.

## 2. Configuración y Puntos de Arranque

### Backend: `config.py` (pydantic-settings)

| Variable | Default | Uso |
| :--- | :--- | :--- |
| `APP_ENV` | `dev` | Etiqueta de logging |
| `API_PORT` | `8000` | Puerto uvicorn |
| `CORS_ORIGINS` | `http://localhost:5173` | Orígenes permitidos (en prod: dominio de Vercel, ver MOD-05 §5) |
| `DB_PATH` | `backend/data/sofredoc.db` | Archivo SQLite |
| `EXTRACTOR_MODE` | `mock` | `mock` \| `llm` (MOD-02) |
| `LLM_PROVIDER` | `openai` | Proveedor de Structured Outputs |
| `LLM_MODEL` | `gpt-4o-mini` | Modelo de extracción |
| `LLM_API_KEY` | *(sin default)* | Requerida si `EXTRACTOR_MODE=llm` |
| `PADRON_PATH` | `backend/data/proveedores.json` | Padrón de proveedores |
| `MAX_PDF_MB` | `5` | Tope de tamaño de subida |
| `TZ` | `America/Argentina/Buenos_Aires` | Zona horaria del reloj del sistema (R5, MOD-01) |

### Backend: `main.py` (app factory)

- Crea la aplicación FastAPI con `title="SofreDoc Validator API"` y `version="0.1.0"`.
- Monta CORS con `CORS_ORIGINS`.
- Registra los routers de `presentation/routers/` (vacíos en este módulo; se completan en MOD-03).
- Expone `GET /api/v1/health`.

```python
# backend/src/main.py (esqueleto)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import get_settings

def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title="SofreDoc Validator API", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # routers de presentation/ se registran aquí a partir de MOD-03
    return app

app = create_app()

@app.get("/api/v1/health")
def health():
    settings = get_settings()
    return {"status": "ok", "version": "0.1.0", "extractor_mode": settings.extractor_mode}
```

### Frontend: scaffold Vite

- `npm create vite@latest frontend -- --template react-ts`
- Tailwind CSS v4 (plugin de Vite) + `lucide-react` para iconografía.
- Carpetas de las 4 capas creadas con `.gitkeep` / archivos semilla.
- Proxy de desarrollo: Vite `server.proxy` redirige `/api` → `http://localhost:8000` (opcional; alternativa: `VITE_API_URL`).

## 3. Contratos de API (HTTP / JSON)

### Endpoint: `GET /api/v1/health`
- **Response `200 OK`:**
```json
{ "status": "ok", "version": "0.1.0", "extractor_mode": "mock" }
```

## 4. Librerías y Dependencias Elegidas

- **Backend:** `fastapi`, `uvicorn[standard]`, `pydantic` (v2), `pydantic-settings`, `python-multipart` (uploads), `pypdf`, `pytest`, `pytest-cov`, `httpx`, `ruff` (dev).
- **Frontend:** `react`, `react-dom`, `typescript`, `vite`, `tailwindcss`, `lucide-react`.
- **Decisiones:** `pypdf` como parser MVP por ser liviano (fallback documentado a `pdfplumber` si los comprobantes requieren lectura de tablas complejas — ver MOD-02 ADR). Sin ORM: `sqlite3` estándar para mantener el PoC liviano.
