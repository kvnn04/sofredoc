# Decisiones de base (sin ID) — MOD-02 a MOD-05: Extracción, API, UI y QA

> **Volver:** [Índice maestro de ADRs](../ADRs.md) · [§4 MOD-02](../modules/02-extraccion-ia/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log) · [§4 MOD-03](../modules/03-api-sqlite/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log) · [§4 MOD-04](../modules/04-frontend/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log) · [§4 MOD-05](../modules/05-qa-testing/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

Consolidado de las **23 decisiones de base** (sin ID) de MOD-02, MOD-03, MOD-04 y MOD-05, con el texto verbatim del §4 de cada módulo (fecha, decisión, motivo e impacto intactos).

## MOD-02: Ingesta PDF y Extracción IA

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | `EXTRACTOR_MODE=mock` como default | Evitar créditos de IA en dev y pruebas k6; demo determinista. | Fixture `extraccion-esperada.json` obligatorio. |
| 2026-11-12 | `pypdf` MVP, `pdfplumber` como fallback | PoC prioriza liviandad; si los PDFs de ejemplo exigen lectura de tablas complejas, se cambia con ADR. | Posible reintento de extracción en Día 4. |
| 2026-11-12 | Máximo 1 reintento de LLM | Balance costo/latencia vs fiabilidad de esquema. | Fallos definitivos → `EXTRACCION_FALLIDA` (502). |
| 2026-11-12 | `json_crudo_ia` persistido junto al resultado | Trazabilidad exigida por CU-03 (inspector de JSON Pydantic). | Columna JSON nullable en SQLite (MOD-03). |
| 2026-11-12 | Proveedor LLM abstracto vía config | Evitar acoplamientos; Structured Outputs es un estándar disponible en varios proveedores. | `client.py` encapsula el SDK. |
| 2026-11-12 | OpenAI `gpt-4o-mini` como proveedor fijado | Confirmado por el product owner (key disponible); Structured Outputs nativo con JSON Schema. | Defaults de `LLM_PROVIDER`/`LLM_MODEL`; cambiar de proveedor solo toca `client.py`. |

## MOD-03: API REST y SQLite

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | `RECHAZADO` responde `200 OK` | El rechazo es un **resultado de negocio** válido; 4xx/5xx reservados a fallos de contrato/infra. | La UI distingue estado del semáforo, no códigos HTTP, para el semáforo. |
| 2026-11-12 | Estado `ERROR_EXTRACCION` solo en tabla | Trazabilidad de fallos sin contaminar el semáforo de reglas. | `reglas_evaluadas=[]` en ese estado. |
| 2026-11-12 | SQLite WAL + `check_same_thread=False` | PoC mono-proceso con concurrencia moderada (k6 50 VUs de solo lectura + escrituras acotadas). | Tope práctico de escrituras concurrentes; suficiente para MVP. |
| 2026-11-12 | PDFs de ejemplo generados por script con fechas relativas | Los ejemplos deben permanecer vigentes (R5: 60 días) sin regeneración manual periódica. | Re-ejecutar `generar_ejemplos.py` si la demo envejece > 60 días. |
| 2026-11-12 | Montos `Decimal` → REAL + JSON numérico 2 decimales | Precisión en dominio; legibilidad en UI. | Conversión explícita en DTOs. |
| 2026-11-12 | Latencia desglosada por etapa (IA / reglas) | Confirmado por el product owner: hace visible la arquitectura híbrida ante el evaluador técnico. | 2 columnas nuevas en SQLite + campos en DTO y UI. |
| 2026-11-12 | SQLite efímero en deploy (free tier) | Render reinicia el disco en cada deploy; el historial es volátil en producción gratuita. | Nota obligatoria en README y smoke post-deploy (MOD-05 §5). |

## MOD-04: Frontend Clean Architecture

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | `fetch` nativo sin axios | 1 API, ~6 endpoints; menos dependencias para un PoC. | Wrapper propio con normalización de errores. |
| 2026-11-12 | Sin router ni store global | Pantalla única con panel de historial; React state + hooks alcanza. | Menos boilerplate; si crece a multi-página, ADR de migración. |
| 2026-11-12 | Visor con `iframe` (sin pdf.js) | Los 3 ejemplos son PDFs digitales simples; pdf.js suma peso innecesario al MVP. | Si aparecen PDFs problemáticos, se evalúa `pdf.js` con ADR. |
| 2026-11-12 | Ejemplos auditados bajando el PDF y re-enviándolo | Un solo contrato de auditoría (`POST /auditar` multipart) sin endpoint "auditar ejemplo" extra. | 1 ida y vuelta extra, despreciable en local. |

## MOD-05: QA Playwright y k6

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | Uso de `EXTRACTOR_MODE=mock` | Evitar llamadas al LLM durante pruebas k6. | Pruebas de estrés deterministas y sin costo. |
| 2026-11-12 | `retries: 0` en Playwright | Los reintentos ocultan flakes (RN-5-06); el reporte debe reflejar la realidad. | Un flake detiene el cierre y se investiga. |
| 2026-11-12 | Clock fijo `2026-11-12` en fixtures unitarios | R5 depende de "hoy"; fecha fija hace los tests reproducibles para siempre. | Regenerar solo si cambia el algoritmo (requiere ADR). |
| 2026-11-12 | Gate de cobertura como parte del DoD | El motor de reglas audita decisiones contables; sin 100% de dominio no hay garantía. | `--cov-fail-under` en el comando oficial. |
| 2026-11-12 | k6 smoke de 10 VUs para CI | Meseta de 50 VUs es lenta para pipeline; el smoke valida regeneración sin exceder tiempos. | Opcional, señal temprana de regresiones. |
| 2026-11-12 | Deploy de cierre en Render + Vercel | Confirmado por el product owner: el MVP debe poder evaluarse sin instalar nada. | SQLite efímero en free tier → historial volátil, documentado. |
