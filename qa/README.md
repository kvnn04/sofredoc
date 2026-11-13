# QA — SofreDoc Validator (MOD-05)

Estrategia de calidad completa: **E2E de UI con Playwright** (`e2e/`) y **pruebas de
carga con k6** (`load/`). Los tests unitarios/integración de backend viven en
`backend/tests/` (ver README raíz, sección Calidad).

```text
qa/
├── e2e/
│   ├── auditoria.spec.ts   # 10 escenarios del flujo (4 obligatorios + 6 extendidos, DESIGN-05 §3)
│   ├── fixtures/           # PDFs del E2E: remito, escaneado sin texto, 11 páginas (ver abajo)
│   ├── reset-db.mjs        # borra la BD efímera antes de cada corrida
│   └── (artefactos en qa/artifacts/, gitignored)
└── load/
    ├── stress_test.js      # k6: rampa a 50 VUs + meseta + drenaje (saturación)
    └── funcional.js        # k6: contrato + matriz de verdad + errores bajo carga
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
# Desde la raíz. Levanta sus PROPIOS procesos en puertos exclusivos del E2E
# (backend mock :8010 con BD efímera + frontend :5175) y corre los 10
# escenarios contra la UI real. No toca ni depende de lo que corras a mano.
npx playwright test qa/e2e/auditoria.spec.ts

# Reporte HTML de la última corrida
npx playwright show-report qa/artifacts/playwright-report

# Regenerar las capturas de la demo para el README (docs/capturas/)
$env:CAPTURAS="1" ; npx playwright test qa/e2e/auditoria.spec.ts ; $env:CAPTURAS=$null

# Regenerar los PDFs fixture del E2E (qa/e2e/fixtures/; commiteados, solo si se edita)
cd backend ; .\.venv\Scripts\python.exe scripts\generar_fixtures_e2e.py ; cd ..
```

Los 10 escenarios (matriz de verdad de MOD-03 en modo mock + extensión ADR-05-08):

1. Ejemplo aprobado → badge `APROBADO`, 5 reglas ✅, desglose de latencia, id `aud_*`.
2. Ejemplo con desvío → badge `RECHAZADO` + `DISCREPANCIA_CONTABLE` (R3).
3. Ejemplo monto alto sin OC → badge `RECHAZADO` + `FALTA_ORDEN_COMPRA` (R4).
4. JSON inspector (Pydantic + crudo IA, copiable) + historial ≥ 3 filas con latencias.
5. Subida propia: `.txt` → `PDF_INVALIDO`, 6 MB → `ARCHIVO_MUY_GRANDE` (client-side, sin
   perder el empty-state) y flujo completo con un PDF real (blob en el visor + "Auditando…").
6. **Remito subido** → admisión **R0**: badge `RECHAZADO`, `REMITO_NO_AUDITABLE` y **1 sola
   regla evaluada** (sin cortocircuito: R1–R5 ni se muestran). Fixture del mock por nombre
   de archivo (`remito…`) → `extraccion-remito.json`.
7. **PDF sin capa de texto** (`qa/e2e/fixtures/pdf-escaneado-grafico.pdf`) → banner
   `PDF_SIN_TEXTO` del backend real (422), sin consumir IA y sin perder el empty-state.
8. **PDF de 11 páginas** (`qa/e2e/fixtures/factura-11-paginas.pdf`) → banner `PDF_INVALIDO`
   (422): el tope de 10 páginas se valida en el backend (client-side pasa).
9. **Red caída** (la llamada se aborta con `page.route`) → banner `ERROR_RED` y el
   resultado previo sigue en pantalla (CU-05).
10. **`EXTRACCION_FALLIDA`** (502 simulado con `page.route`, el backend no recibe nada) →
    banner tipado con el código del contrato y resultado previo intacto (CU-05).

Notas:

- **`retries: 0`** (RN-5-06): un flake detiene la corrida y se investiga; no se
  reintenta a ciegas.
- **Puertos exclusivos del E2E (ADR-05-09):** backend **:8010** (mock, BD efímera
  `qa/artifacts/e2e-sofredoc.db`) y frontend **:5175** (su proxy `/api` apunta al
  backend del E2E vía `VITE_PROXY_TARGET`), con `reuseExistingServer: false`.
  Podés correr los tests con tu instancia manual arriba (`:8000`/`:5173`) sin
  interferencia: antes, si el backend manual estaba en modo `llm`, Playwright lo
  reutilizaba y la matriz de verdad mock no aplicaba (bug visto en el escenario 2).
- Chromium headless no renderiza PDFs en línea: el visor queda en blanco en el
  E2E, pero el flujo de auditoría es completo (limitación del navegador, no del
  producto).

## Carga — k6 (RN-5-01: exclusivamente `EXTRACTOR_MODE=mock`)

Dos scripts complementarios (ADR-05-10): `stress_test.js` mide **saturación**
(techo de concurrencia) y `funcional.js` mide **correctitud del contrato** bajo
carga moderada (los 200 tienen que devolver el contenido correcto, no solo un
status OK).

```powershell
# Terminal 1 — backend mock con BD efímera (desde backend/)
node ../qa/e2e/reset-db.mjs
$env:DB_PATH="qa/artifacts/k6-sofredoc.db"
.\.venv\Scripts\python.exe -m uvicorn src.main:app --port 8000

# Terminal 2 — saturación: rampa 30 s a 50 VUs, meseta 1 min, drenaje 15 s
k6 run qa/load/stress_test.js

# Smoke de saturación para CI (10 VUs × 30 s, mismo script con env SMOKE=1)
$env:SMOKE="1" ; k6 run qa/load/stress_test.js ; $env:SMOKE=$null
```

### Funcional — `funcional.js` (ADR-05-10)

Valida el **contrato de la API** bajo carga: 3 escenarios en paralelo (~2 min),
seleccionables con `ESCENARIO` (default `todo`) y modo smoke corto para CI:

```powershell
# Corrida completa: contrato (10 VUs) + matriz (2 VUs) + errores (2 VUs), ~2 min
$env:BASE_URL="http://localhost:8000/api/v1" ; k6 run qa/load/funcional.js ; $env:BASE_URL=$null

# Smoke para CI (~30 s, perfiles reducidos)
$env:SMOKE="1" ; k6 run qa/load/funcional.js ; $env:SMOKE=$null

# Un solo escenario
$env:ESCENARIO="matriz"  ; k6 run qa/load/funcional.js ; $env:ESCENARIO=$null
$env:ESCENARIO="errores" ; k6 run qa/load/funcional.js ; $env:ESCENARIO=$null
```

Qué valida cada escenario (con `check`, no solo status):

| Escenario | Validaciones |
| :--- | :--- |
| `contrato` | Los 6 endpoints: health en modo mock, catálogo con `resultado_esperado`, PDFs con magia `%PDF`, auditoría con id `aud_*` + latencias numéricas, historial **sin** `json_crudo_ia`, detalle **con** `json_crudo_ia` |
| `matriz` | Los 3 ejemplos + el remito fixture del E2E (fuente única, `qa/e2e/fixtures/`): APROBADO con 5 reglas ✅, RECHAZADO solo-R3, solo-R4 y remito con exactamente 1 regla (R0) |
| `errores` | `.txt` → 422 `PDF_INVALIDO` · blob 5.5 MB → 413 `ARCHIVO_MUY_GRANDE` · historial inexistente → 404 `AUDITORIA_NO_ENCONTRADA` · ejemplo inexistente → 404 `EJEMPLO_NO_ENCONTRADO` |

Umbrales: `checks` > 99% (un 200 con JSON malformado cuenta como fallo) y p95
< 500 ms. `http_req_failed` se thresholdiza **por escenario** (`{scenario:...}`
en `contrato` y `matriz`): en `errores` todos los requests son 4xx esperados.

Nota de diseño: **pausa de 1 s por iteración** — carga concurrente moderada que
no satura el lock de la SQLite compartida (techo ~165 req/s, ADR-05-06). La
saturación la mide `stress_test.js`; este script mide correctitud.

Umbrales (SLOs de `02-design.md` §3, verificables en `04-verification.md` §3):

| Métrica | Umbral |
| :--- | :--- |
| Tasa de error (`http_req_failed`) | < 1% |
| Latencia p95 (`http_req_duration`) | < 500 ms |
| Concurrencia objetivo | 50 VUs (30 s de rampa + 60 s de meseta) |
