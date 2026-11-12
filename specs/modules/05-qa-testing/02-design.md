# DESIGN-05: QA: Pytest, Playwright & k6 — Diseño Técnico

> **Audiencia:** Ingenieros de Software, Agentes de IA.
> **Patrón:** Clean Architecture (Monolito FastAPI + React).

## 1. Arquitectura de Componentes y Capas

```text
sofredoc-validator/
├── backend/tests/
│   ├── unit/                        # Dominio, reglas, extractor (falsificado), engine
│   │   ├── test_cuit.py  test_reglas.py  test_engine.py
│   │   ├── test_extractor.py  test_smoke.py
│   │   └── conftest.py              # factory factura(**overrides), clock fijo, padrón stub
│   └── integration/
│       ├── test_api_auditar.py      # TestClient + SQLite temporal + extractor mock
│       ├── test_api_historial.py
│       └── conftest.py              # app con DB_PATH=tmp, EXTRACTOR_MODE=mock
├── qa/
│   ├── e2e/
│   │   └── auditoria.spec.ts        # Playwright (UI contra backend+frontend reales)
│   └── load/
│       └── stress_test.js           # k6
├── playwright.config.ts             # (raíz) baseURL, retries, reporte HTML
└── package.json (raíz, opcional)    # devDependency @playwright/test
```

La regla de dependencias de tests: `unit` no depende de red ni de archivos grandes; `integration` depende solo de la app FastAPI y SQLite temporal; `e2e` depende de los 3 procesos/servicios reales levantados a mano (o por `webServer` de Playwright).

## 2. Modelos de Datos y Esferas de Dominio

### Fixtures clave (conftest.py)

```python
# backend/tests/unit/conftest.py (esencia)
import pytest
from datetime import date
from src.domain.models import FacturaExtraida

BASE_VALIDA = dict(
    tipo_comprobante="FACTURA",
    numero_comprobante="A-0001-00000123",
    cuit_emisor="30-12345678-1",
    razon_social="Distribuidora Andina S.A.",
    fecha_emision=date(2026, 11, 7),          # clock fijo: hoy = 2026-11-12
    numero_orden_compra="OC-2026-0441",
    items=[{"descripcion": "Servicio", "cantidad": 2, "precio_unitario": "175000", "subtotal": "350000"}],
    impuestos="34000",
    monto_total="384000",
)

@pytest.fixture
def factura():
    def _factory(**overrides) -> FacturaExtraida:
        return FacturaExtraida(**{**BASE_VALIDA, **overrides})
    return _factory
```

### Esquema de Base de Datos (SQLite)

No aplica (usa el esquema de MOD-03; los tests de integración apuntan a un archivo temporal con el mismo DDL).

## 3. Contratos de API (HTTP / JSON)

Los tests E2E y de carga consumen los contratos de MOD-03 §3. Scripts de referencia:

### `qa/e2e/auditoria.spec.ts` — escenarios

```typescript
// 4 escenarios obligatorios (datos de la matriz de ejemplos de MOD-03):
// 1) ejemplo aprobado   → badge "APROBADO" + 5 reglas ✅
// 2) ejemplo desvío     → badge "RECHAZADO" + "DISCREPANCIA_CONTABLE" visible
// 3) ejemplo sin OC     → badge "RECHAZADO" + "FALTA_ORDEN_COMPRA" visible
// 4) JSON + historial   → JSON inspector desplegable visible (Pydantic + crudo IA);
//                        historial con ≥ 3 filas y desglose de latencia (IA/reglas/total) en el badge
```

```typescript
// playwright.config.ts (esencia)
export default defineConfig({
  testDir: "./qa/e2e",
  timeout: 30_000,
  retries: 0,                 // RN-5-06: sin máscara de flakes
  use: { baseURL: "http://localhost:5173" },
  reporter: [["html", { open: "never" }]],
  // webServer opcional para levantar backend (uvicorn mock) y frontend (vite preview)
});
```

```bash
npx playwright test qa/e2e/auditoria.spec.ts
```

### `qa/load/stress_test.js` — k6

```javascript
import http from "k6/http";
import { check } from "k6";

export const options = {
  stages: [
    { duration: "30s", target: 50 },   // rampa
    { duration: "1m",  target: 50 },   // meseta (concurrencia objetivo)
    { duration: "15s", target: 0 },    // drenaje
  ],
  thresholds: {
    http_req_failed:   ["rate<0.01"],     // < 1% errores
    http_req_duration: ["p(95)<500"],     // p95 < 500 ms
  },
};

const BASE = __ENV.BASE_URL || "http://localhost:8000/api/v1";
const PDF = open("../../backend/data/ejemplos/factura-aprobada-001.pdf", "b");

export default function () {
  // Auditoría (mock) — flujo principal
  const res = http.post(`${BASE}/auditar`, { file: http.file(PDF, "factura.pdf", "application/pdf") });
  check(res, { "auditar 200": (r) => r.status === 200, "con reglas": (r) => r.json("reglas_evaluadas").length === 5 });
  // Lecturas
  check(http.get(`${BASE}/historial?limit=10`), { "historial 200": (r) => r.status === 200 });
  check(http.get(`${BASE}/ejemplos`), { "ejemplos 200": (r) => r.status === 200 });
}
```

```bash
# Requisito: backend con EXTRACTOR_MODE=mock (RN-5-01)
EXTRACTOR_MODE=mock uvicorn src.main:app --port 8000
k6 run qa/load/stress_test.js
```

### Umbrales (SLOs / SLAs)

| Métrica | Umbral |
| :--- | :--- |
| Tasa de error (`http_req_failed`) | < 1% |
| Latencia p95 (`http_req_duration`) | < 500 ms (modo mock) |
| Concurrencia objetivo | 50 usuarios virtuales simultáneos |
| Suite Pytest completo | < 30 s |

## 4. Librerías y Dependencias Elegidas

- Backend: `pytest`, `pytest-cov`, `httpx` (TestClient). Cliente LLM falsificado (stub en `conftest`), sin `responses`/`vcr` (la frontera ya es un puerto).
- E2E: `@playwright/test` (Chromium por defecto).
- Carga: `k6` (binario CLI). Reportes versionados bajo `qa/artifacts/` (gitignored).

## 5. Despliegue de Cierre (Render + Vercel)

Confirmado con el product owner (2026-11-12): el MVP se despliega como cierre de este módulo.

| Pieza | Plataforma | Configuración clave |
| :--- | :--- | :--- |
| Backend | **Render** (free tier) | Build: `pip install -r requirements.txt` · Start: `uvicorn src.main:app --host 0.0.0.0 --port $PORT` · Env: `EXTRACTOR_MODE`, `LLM_PROVIDER`/`LLM_MODEL`/`LLM_API_KEY`, `CORS_ORIGINS=https://<dominio-vercel>` |
| Frontend | **Vercel** | Build: `npm run build` · Env: `VITE_API_URL=https://<backend>.onrender.com/api/v1` |

- **Nota SQLite efímero:** el free tier de Render reinicia el disco en cada deploy → el historial se vacía. Aceptable para la PoC y documentado en el README (persistencia real requeriría disco persistente o Postgres, fuera de alcance).
- **Smoke post-deploy:** `GET /api/v1/health` → 200, y `POST /auditar` con el ejemplo #001 en modo mock → `APROBADO`.
- Los 3 PDFs de ejemplo y el padrón viajan en el repo (no requieren almacenamiento externo).
