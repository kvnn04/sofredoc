# TASKS-05: QA: Pytest, Playwright & k6 — Plan de Ejecución

> **Instrucción para la IA:** Ejecutar las tareas en orden estricto de dependencias. Tras completar cada tarea, marcar la casilla con `[x]` y asegurar que las pruebas sigan pasando.

## Fase 1: Organización de Suites Pytest

- [x] **T-01:** Reorganizar `backend/tests/` en `unit/` + `integration/` con `__init__.py` y `conftest.py` por capa (fixtures `factura(**overrides)`, clock fijo `2026-11-12`, padrón stub). *(Estructura ya creada en MOD-01..03; verificada en esta sesión.)*
- [x] **T-02:** Migrar/verificar que los tests de MOD-01 (reglas + CUIT + engine) y MOD-02 (extractor) viven en `unit/` y siguen en verde.
- [x] **T-03:** Configurar el gate de cobertura: `pytest backend/tests --cov=src --cov-fail-under=95 --cov-report=term-missing` con los gates por carpeta exigidos (dominio 100%, aplicación > 90%) — los de `integration` cuentan en la medición de `application/`.
- [x] **T-04:** Asegurar que `integration/` usa SQLite en archivo temporal y `EXTRACTOR_MODE=mock` (ninguna llamada de red en ningún test).

## Fase 2: E2E con Playwright

- [x] **T-05:** Configurar Playwright en la raíz: `playwright.config.ts` (baseURL `http://localhost:5173`, Chromium, `retries: 0`, reporter HTML) y devDependency `@playwright/test`.
- [x] **T-06:** Implementar `qa/e2e/auditoria.spec.ts` con los 4 escenarios obligatorios de `02-design.md` §3 (3 ejemplos con sus estados esperados + JSON inspector/historial). *(Requirió ADR-05-01: el mock resuelve la fixture por identidad del ejemplo.)*
- [x] **T-07:** Correr la suite dos veces consecutivas en verde (verificación anti-flake) y versionar `qa/README.md` con instrucciones de ejecución (backend mock + frontend + `npx playwright test`).

## Fase 3: Pruebas de Carga con k6

- [x] **T-08:** Implementar `qa/load/stress_test.js` con las 3 etapas (rampa 50 VUs, meseta 1 min, drenaje) y los thresholds de `02-design.md` §3.
- [x] **T-09:** Ejecutar `k6 run qa/load/stress_test.js` contra backend mock y registrar los resultados reales (p50, p95, tasa de error, iteraciones/s) en la tabla de resultados de `04-verification.md`.
- [x] **T-10:** Smoke de carga ligero opcional para CI: `target: 10 VUs, duration: 30s` (mismo script con `options.vus` sobreescrito por env `SMOKE=1`).

## Fase 4: Integración y Cierre

- [x] **T-11:** Workflow opcional de verificación (GitHub Actions): job único que corre `pytest` → `npm run build` → `playwright` → `k6 run` en modo smoke, con reportes como artefactos. *(`.github/workflows/verificacion.yml`; se corrigió el `webServer` de Playwright para ser cross-platform.)*
- [x] **T-12:** Completar el ADR Log y el Definition of Done de `04-verification.md`; actualizar la tabla de estado de `specs/README.md` (módulos 🟢). *(ADR-05-01..06; el 🟢 de MOD-05 queda supeditado al deploy de Fase 5 → 🟡.)*
- [x] **T-13:** Actualizar el `README.md` raíz con la sección "Calidad" (comandos de pytest, playwright, k6 y umbrales) y capturas de la demo (Día 4 del plan original). *(Capturas reales del E2E en `docs/capturas/`.)*

## Fase 5: Despliegue de Cierre

- [ ] **T-14:** Desplegar el backend en Render (build/start commands + variables `EXTRACTOR_MODE`, credenciales LLM, `CORS_ORIGINS` del dominio de Vercel) y verificar `GET /api/v1/health` público.
- [ ] **T-15:** Desplegar el frontend en Vercel con `VITE_API_URL` apuntando al backend de Render; verificar que no hay errores de CORS.
- [ ] **T-16:** Smoke post-deploy: `health` 200 + auditar el ejemplo #001 (mock) + historial visible; documentar URLs y la nota de SQLite efímero en el README.
