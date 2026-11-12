# QA — SofreDoc Validator (MOD-05)

Estrategia de calidad completa: **E2E de UI con Playwright** (`e2e/`) y **pruebas de
carga con k6** (`load/`). Los tests unitarios/integración de backend viven en
`backend/tests/` (ver README raíz, sección Calidad).

```text
qa/
├── e2e/
│   ├── auditoria.spec.ts   # 4 escenarios obligatorios del flujo demo (DESIGN-05 §3)
│   ├── reset-db.mjs        # borra la BD efímera antes de cada corrida
│   └── (artefactos en qa/artifacts/, gitignored)
└── load/
    └── stress_test.js      # k6: rampa a 50 VUs + meseta + drenaje
```

## Prerrequisitos (una vez)

```powershell
# En la raíz del repo (dependencias de E2E + navegador Chromium)
npm install
npx playwright install chromium

# Backend: venv con dependencias (ver README raíz)
cd backend ; python -m venv .venv ; .\.venv\Scripts\Activate ; pip install -r requirements.txt
```

## E2E — Playwright

```powershell
# Desde la raíz. Levanta solo los 2 procesos (backend mock + frontend Vite)
# con `webServer` y corre los 4 escenarios contra la UI real.
npx playwright test qa/e2e/auditoria.spec.ts

# Reporte HTML de la última corrida
npx playwright show-report qa/artifacts/playwright-report

# Regenerar las capturas de la demo para el README (docs/capturas/)
$env:CAPTURAS="1" ; npx playwright test qa/e2e/auditoria.spec.ts ; $env:CAPTURAS=$null
```

Los 4 escenarios (matriz de verdad de MOD-03 en modo mock):

1. Ejemplo aprobado → badge `APROBADO`, 5 reglas ✅, desglose de latencia, id `aud_*`.
2. Ejemplo con desvío → badge `RECHAZADO` + `DISCREPANCIA_CONTABLE` (R3).
3. Ejemplo monto alto sin OC → badge `RECHAZADO` + `FALTA_ORDEN_COMPRA` (R4).
4. JSON inspector (Pydantic + crudo IA, copiable) + historial ≥ 3 filas con latencias.

Notas:

- **`retries: 0`** (RN-5-06): un flake detiene la corrida y se investiga; no se
  reintenta a ciegas.
- **RN-5-05:** el backend del E2E usa `DB_PATH=qa/artifacts/e2e-sofredoc.db`
  (gitignored) y lo resetea al arrancar. Nunca toca la BD real
  `backend/data/sofredoc.db`. Si preferís correr el backend a mano y que
  Playwright lo reutilice (`reuseExistingServer` en local), arrancalo con esa
  misma `DB_PATH` efímera.
- Chromium headless no renderiza PDFs en línea: el visor queda en blanco en el
  E2E, pero el flujo de auditoría es completo (limitación del navegador, no del
  producto).

## Carga — k6 (RN-5-01: exclusivamente `EXTRACTOR_MODE=mock`)

```powershell
# Terminal 1 — backend mock con BD efímera (desde backend/)
node ../qa/e2e/reset-db.mjs
$env:DB_PATH="qa/artifacts/k6-sofredoc.db"
.\.venv\Scripts\python.exe -m uvicorn src.main:app --port 8000

# Terminal 2 — prueba de carga completa (rampa 30 s a 50 VUs, meseta 1 min, drenaje 15 s)
k6 run qa/load/stress_test.js

# Smoke para CI (10 VUs × 30 s, mismo script con env SMOKE=1)
$env:SMOKE="1" ; k6 run qa/load/stress_test.js ; $env:SMOKE=$null
```

Umbrales (SLOs de `02-design.md` §3, verificables en `04-verification.md` §3):

| Métrica | Umbral |
| :--- | :--- |
| Tasa de error (`http_req_failed`) | < 1% |
| Latencia p95 (`http_req_duration`) | < 500 ms |
| Concurrencia objetivo | 50 VUs (30 s de rampa + 60 s de meseta) |
