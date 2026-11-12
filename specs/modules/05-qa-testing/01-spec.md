# SPEC-05: QA: Pytest, Playwright & k6 — Requisitos y Alcance

> **Audiencia:** Producto, Negocio, Revisor Técnico.
> **Estado:** Draft / Approved / In Progress / Completed

## 1. Problema de Negocio

Una PoC técnica se juega su credibilidad en la **confiabilidad demostrable**: si el evaluador ve un test rojo, un flake o una latencia errática, la propuesta pierde valor comercial. Además, el motor de reglas audita decisiones contables: no hay margen para "casi correcto".

Este módulo consolida la **estrategia de calidad completa** del sistema: pruebas unitarias e integración (Pytest), pruebas end-to-end de UI (Playwright) y pruebas de carga (k6 en modo mock, sin créditos de IA), con umbrales objetivos (SLOs) y criterio de cierre (Definition of Done).

## 2. Objetivos

- [ ] Suite Pytest organizado en `unit/` + `integration/` con cobertura: dominio **100%**, aplicación **> 90%**.
- [ ] Suite Playwright con los 4 escenarios E2E del flujo de auditoría, sin flakes (2 pasadas consecutivas verdes).
- [ ] Script k6 con `EXTRACTOR_MODE=mock`: 50 usuarios virtuales, tasa de error < 1%, p95 < 500 ms.
- [ ] Estructura `qa/` (e2e + load) versionada y documentada en el README raíz.
- [ ] Despliegue de cierre: backend en **Render** + frontend en **Vercel** con smoke post-deploy (health + auditoría de ejemplo).

## 3. Reglas de Negocio y Restricciones

- **RN-5-01:** Las pruebas de carga (k6) corren **exclusivamente** con `EXTRACTOR_MODE=mock`: determinismo y costo cero de IA.
- **RN-5-02:** Los tests unitarios/integración de backend **nunca** llaman a la red ni a la API real del LLM (cliente falsificado); los de integración usan SQLite en archivo temporal.
- **RN-5-03:** Cobertura mínima con gate: `domain/` 100%, `application/` > 90%; el resto es informativo.
- **RN-5-04:** Los tests E2E usan datos de los 3 ejemplos pre-cargados (resultados esperados conocidos: APROBADO / RECHAZADO-R3 / RECHAZADO-R4).
- **RN-5-05:** Ningún test modifica `backend/data/sofredoc.db` real ni deja artefactos en el repo (fixtures temporales, `.gitignore` de reportes).
- **RN-5-06:** Un test que falla de forma intermitente (flake) se trata como test rojo: se investiga, no se reintenta a ciegas.

## 4. Casos de Uso (Given-When-Then)

### CU-01: Verificación rápida del desarrollador (antes de commitear)
- **Given** el backend con cambios en reglas o extractor
- **When** se ejecuta `pytest backend/tests -v`
- **Then** todo pasa en verde en < 30 s sin red y la cobertura del dominio se mantiene en 100%.

### CU-02: Verificación E2E del flujo demo
- **Given** backend (mock) y frontend corriendo en local
- **When** se ejecuta `npx playwright test qa/e2e/auditoria.spec.ts`
- **Then** los 4 escenarios (3 ejemplos + historial/JSON) pasan y generan el reporte HTML.

### CU-03: Prueba de carga sin créditos
- **Given** el backend corriendo con `EXTRACTOR_MODE=mock`
- **When** se ejecuta `k6 run qa/load/stress_test.js` (rampa a 50 VUs)
- **Then** `http_req_failed < 1%` y `p(95) < 500 ms` sobre `/auditar` (mock) y `/historial`.

### CU-04: Cierre formal del proyecto (Definition of Done)
- **Given** todos los módulos implementados
- **When** se revisa el checklist final de este documento
- **Then** cada módulo del índice (`specs/README.md`) puede marcarse 🟢 Completado con su ADR log completo.

## 5. Fuera de Alcance (Out of Scope)

- CI/CD completo con despliegues automáticos (solo workflow opcional de verificación; el deploy de cierre es manual/scriptado, ver §5 del design).
- Pruebas de carga contra el modo `llm` (costo y no-determinismo).
- Security testing (pentest, SAST/DAST profundos); solo higiene básica (no secretos en repo).
- Cross-browser exhaustivo (Playwright corre en Chromium; Firefox/WebKit opcionales).
- Property-based testing / fuzzing.
