# VERIFICATION-05: QA: Pytest, Playwright & k6 — Testing y Cierre

> **Audiencia:** QA, Lead Developer, CI/CD.

## 1. Pruebas Unitarias e Integración (Pytest)

```bash
# Correr pruebas de dominio y reglas
pytest backend/tests/unit -v

# Correr pruebas integradas de API y base de datos
pytest backend/tests/integration -v

# Suite completo + gate de cobertura
pytest backend/tests -v --cov=src --cov-report=term-missing --cov-fail-under=95
```

### Cobertura Mínima Requerida
- Domain / Rules Engine: **100%**
- Application / Use Cases: **> 90%**
- Infrastructure (db, pdf, llm adapters): > 90%
- Tiempo del suite completo: < 30 s (sin red).

## 2. Pruebas E2E (Playwright)

```bash
npx playwright test qa/e2e/auditoria.spec.ts
```

- [ ] Verificar la carga de los 3 ejemplos pre-cargados (resultados: APROBADO / RECHAZADO-R3 / RECHAZADO-R4).
- [ ] Confirmar actualización visual del semáforo (`APROBADO` vs `RECHAZADO`).
- [ ] Validar visualización del panel de JSON Pydantic (plegado → desplegado → copiable, Pydantic + crudo IA).
- [ ] Verificar el desglose de latencia por etapa (IA / reglas / total) junto al badge de estado.
- [ ] Historial: ≥ 3 filas tras los 3 escenarios, con latencia en ms y recarga de detalle.
- [ ] Dos pasadas consecutivas en verde (cero flakes, `retries: 0`).

## 3. Pruebas de Estrés y Rendimiento (k6)

Ejecutar k6 en modo `EXTRACTOR_MODE=mock` para evaluar concurrencia y la base SQLite sin consumir créditos de IA:

```bash
EXTRACTOR_MODE=mock uvicorn src.main:app --port 8000 &
k6 run qa/load/stress_test.js
```

### Umbrales (SLOs / SLAs)

Corrida completa (T-09, 2026-11-12): backend uvicorn `EXTRACTOR_MODE=mock` en `:8000` con
`DB_PATH=qa/artifacts/k6-sofredoc.db` (efímera, RN-5-05). Escenario: rampa 30 s a 50 VUs,
meseta 60 s, drenaje 15 s (105 s totales). Throughput: **164,95 req/s** (17.322 requests,
5.774 iteraciones a 54,98/s), 23.096/23.096 checks OK.

| Métrica | Umbral | Resultado obtenido | ✅/❌ |
| :--- | :--- | :--- | :---: |
| Tasa de error (`http_req_failed`) | < 1% | **0.00%** (0 de 17.322 requests) | ✅ |
| Latencia p95 (`http_req_duration`) | < 500 ms | **449.35 ms** (p50 = 239.08 ms) | ✅ |
| Concurrencia objetivo | 50 VUs | 50 VUs en meseta (60 s) | ✅ |

Smoke para CI (T-10, `SMOKE=1`): 10 VUs × 30 s → p95 **71.93 ms**, tasa de error **0.00%**,
1.521 iteraciones (50,5/s), 6.084/6.084 checks OK.

Observación: a 50 VUs el p95 (449 ms) queda cerca del umbral: el cuello de botella es la
conexión SQLite compartida con lock (el repositorio serializa inserts y lecturas), no la
extracción mock (< 10 ms). Para la PoC es aceptable; escalar a Postgres/pool de conexiones
está fuera de alcance (nota de DESIGN-05 §5).

## 4. Registro de Decisiones de Arquitectura (ADR Log)

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | Uso de `EXTRACTOR_MODE=mock` | Evitar llamadas al LLM durante pruebas k6. | Pruebas de estrés deterministas y sin costo. |
| 2026-11-12 | `retries: 0` en Playwright | Los reintentos ocultan flakes (RN-5-06); el reporte debe reflejar la realidad. | Un flake detiene el cierre y se investiga. |
| 2026-11-12 | Clock fijo `2026-11-12` en fixtures unitarios | R5 depende de "hoy"; fecha fija hace los tests reproducibles para siempre. | Regenerar solo si cambia el algoritmo (requiere ADR). |
| 2026-11-12 | Gate de cobertura como parte del DoD | El motor de reglas audita decisiones contables; sin 100% de dominio no hay garantía. | `--cov-fail-under` en el comando oficial. |
| 2026-11-12 | k6 smoke de 10 VUs para CI | Meseta de 50 VUs es lenta para pipeline; el smoke valida regeneración sin exceder tiempos. | Opcional, señal temprana de regresiones. |
| 2026-11-12 | Deploy de cierre en Render + Vercel | Confirmado por el product owner: el MVP debe poder evaluarse sin instalar nada. | SQLite efímero en free tier → historial volátil, documentado. |

## 5. Criterio de Aceptación Final (Definition of Done) — Proyecto Completo

- [ ] Todas las tareas de `03-tasks.md` de **los 6 módulos** están marcadas como `[x]`.
- [ ] Todos los tests de Pytest pasan en verde (`unit` + `integration`, < 30 s, sin red).
- [ ] Cobertura: dominio 100%, aplicación > 90% (gate activo).
- [ ] Los tests de Playwright se ejecutan correctamente sin flakiness (2 pasadas).
- [ ] k6 cumple con los SLAs de latencia (p95 < 500 ms) y tasa de error (< 1%) con 50 VUs en modo mock.
- [ ] Los 3 PDFs de ejemplo son válidos y vigentes (fechas dentro de los 60 días de R5).
- [ ] La demo completa corre de cero con 2 comandos (backend + frontend) en < 15 s de setup post-instalación.
- [ ] `specs/README.md` refleja el estado real (🟢 Completado) y cada `04-verification.md` tiene su ADR log completo.
- [ ] Backend y frontend desplegados (Render + Vercel) con smoke post-deploy en verde y URLs documentadas.
- [ ] `README.md` raíz con quickstart, arquitectura, sección de calidad y capturas de la demo.
