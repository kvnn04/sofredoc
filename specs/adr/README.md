# Índice de ADRs — Decisiones de Arquitectura

Índice único de las **71 decisiones** de arquitectura de SofreDoc Validator: **33 ADRs numerados** + **38 de base** (sin ID). Cada fila abre el archivo con el texto completo (fecha, decisión, motivo e impacto); las de base viven en los 2 consolidados de esta carpeta.

> El texto completo vive en esta carpeta: `adr-XX-YY-*.md` (uno por ADR numerado) y `base-*.md` (consolidados por módulo). El §4 de cada `04-verification.md` mantiene una tabla resumen con links. Orden de la tabla: por módulo (MOD-00 → MOD-05); dentro de cada uno, numerados por ID y luego las de base.

| ID | Fecha | Módulo | Descripción breve | Archivo |
| :--- | :--- | :--- | :--- | :--- |
| — | 2026-11-12 | MOD-00 | Migrar de `backend/app/` plano a Clean Architecture `backend/src/` | [→](base-00-01-core-y-reglas.md#mod-00-arquitectura-monolito-y-core) |
| — | 2026-11-12 | MOD-00 | `pypdf` como parser PDF del MVP (fallback: `pdfplumber`) | [→](base-00-01-core-y-reglas.md#mod-00-arquitectura-monolito-y-core) |
| — | 2026-11-12 | MOD-00 | Sin ORM: `sqlite3` stdlib | [→](base-00-01-core-y-reglas.md#mod-00-arquitectura-monolito-y-core) |
| — | 2026-11-12 | MOD-01 | `Decimal` en el dominio (no `float`) | [→](base-00-01-core-y-reglas.md#mod-01-dominio-y-motor-de-reglas) |
| — | 2026-11-12 | MOD-01 | Variante Módulo 11: dv=11→0, dv=10→9 | [→](base-00-01-core-y-reglas.md#mod-01-dominio-y-motor-de-reglas) |
| — | 2026-11-12 | MOD-01 | Evaluación de las 5 reglas siempre completa (sin cortocircuito) | [→](base-00-01-core-y-reglas.md#mod-01-dominio-y-motor-de-reglas) |
| — | 2026-11-12 | MOD-01 | `ClockPort` inyectable | [→](base-00-01-core-y-reglas.md#mod-01-dominio-y-motor-de-reglas) |
| — | 2026-11-12 | MOD-01 | Reloj de sistema en `America/Argentina/Buenos_Aires` | [→](base-00-01-core-y-reglas.md#mod-01-dominio-y-motor-de-reglas) |
| — | 2026-11-12 | MOD-01 | Regla de admisión R0 (remitos) | [→](base-00-01-core-y-reglas.md#mod-01-dominio-y-motor-de-reglas) |
| — | 2026-11-12 | MOD-01 | Dependencia `tzdata` con marcador `sys_platform == "win32"` | [→](base-00-01-core-y-reglas.md#mod-01-dominio-y-motor-de-reglas) |
| — | 2026-11-12 | MOD-01 | Sintaxis `X \| None` (PEP 604) + `collections.abc.Sequence` | [→](base-00-01-core-y-reglas.md#mod-01-dominio-y-motor-de-reglas) |
| — | 2026-11-12 | MOD-01 | `Proveedor` definido en `domain/ports/padron_port.py` | [→](base-00-01-core-y-reglas.md#mod-01-dominio-y-motor-de-reglas) |
| — | 2026-11-12 | MOD-01 | `digito_verificador_valido` retorna `False` si el formato es inválido | [→](base-00-01-core-y-reglas.md#mod-01-dominio-y-motor-de-reglas) |
| — | 2026-11-12 | MOD-01 | `detalles` tipado `dict[str, str]`; montos es-AR vía `formato_ars` | [→](base-00-01-core-y-reglas.md#mod-01-dominio-y-motor-de-reglas) |
| — | 2026-11-12 | MOD-01 | Fixture factory `factura(**overrides)` en `tests/unit/conftest.py` | [→](base-00-01-core-y-reglas.md#mod-01-dominio-y-motor-de-reglas) |
| ADR-02-01 | 2026-11-12 | MOD-02 | `openai>=1.40` agregada a `requirements.txt` (el design la declaraba pero faltaba en el archivo) | [→](adr-02-01-openai-agregada-a-requirements.md) |
| ADR-02-02 | 2026-11-12 | MOD-02 | Errores de extracción como excepciones puras en `domain/errors.py` con atributo `codigo` (capturables sin acoplarse a adaptadores) | [→](adr-02-02-errores-de-extraccion-en-el-dominio.md) |
| ADR-02-03 | 2026-11-12 | MOD-02 | `preparar_esquema_estricto()` limpia el JSON Schema de Pydantic para el modo `strict` del proveedor | [→](adr-02-03-esquema-estricto-structured-outputs.md) |
| ADR-02-04 | 2026-11-12 | MOD-02 | Fallo del proveedor LLM se tipifica y NO se reintenta (reintento solo sobre `ValidationError`) | [→](adr-02-04-fallo-del-proveedor-no-se-reintenta.md) |
| ADR-02-05 | 2026-11-12 | MOD-02 | `MOCK_VARIANT` como 12ª variable de config (default `aprobada`) | [→](adr-02-05-mock-variant-en-config.md) |
| ADR-02-06 | 2026-11-12 | MOD-02 | Fixture mock con fecha estática `2026-11-07` (la demo caduca por R5 ≈ 2027-01-06; regenerar antes) | [→](adr-02-06-fixture-mock-fecha-estatica.md) |
| ADR-02-07 | 2026-11-12 | MOD-02 | SDK importado en perezoso + umbral de 20 caracteres significativos (el mock corre sin `openai` instalado) | [→](adr-02-07-sdk-importado-lazy.md) |
| ADR-02-08 | 2026-11-13 | MOD-02 | `Decimal` del esquema colapsado a rama `number` en strict (con LLM real el proveedor elegía la rama string → `EXTRACCION_FALLIDA`) | [→](adr-02-08-decimal-colapsado-a-rama-numerica.md) |
| ADR-02-09 | 2026-11-13 | MOD-02 | p95 de extracción real ≈ 10.8 s > umbral de laboratorio (8 s): desvío aceptado (varianza del proveedor; motor < 10 ms) | [→](adr-02-09-p95-de-extraccion-desvio-aceptado.md) |
| ADR-02-10 | 2026-11-14 | MOD-02 | Descripciones AFIP campo por campo + reglas de prompt (Factura A con IVA discriminado dejaba de dar falso positivo) | [→](adr-02-10-semantica-afip-en-esquema-y-prompt.md) |
| ADR-02-11 | 2026-11-14 | MOD-02 | `letra_comprobante` + prompt por letra (el recuado de Transparencia Fiscal, Ley 27.743, en B ya viene incluido en el total) | [→](adr-02-11-letra-de-comprobante-y-ley-27743.md) |
| ADR-02-12 | 2026-11-14 | MOD-02 | `detalle_impuestos` línea a línea + `impuestos` recalculado en Python + gate de consistencia pre-reintento (ecuación de R3) | [→](adr-02-12-impuestos-calculado-en-python.md) |
| — | 2026-11-12 | MOD-02 | `EXTRACTOR_MODE=mock` como default | [→](base-02-05-extraccion-api-ui-qa.md#mod-02-ingesta-pdf-y-extracción-ia) |
| — | 2026-11-12 | MOD-02 | `pypdf` MVP, `pdfplumber` como fallback | [→](base-02-05-extraccion-api-ui-qa.md#mod-02-ingesta-pdf-y-extracción-ia) |
| — | 2026-11-12 | MOD-02 | Máximo 1 reintento de LLM | [→](base-02-05-extraccion-api-ui-qa.md#mod-02-ingesta-pdf-y-extracción-ia) |
| — | 2026-11-12 | MOD-02 | `json_crudo_ia` persistido junto al resultado | [→](base-02-05-extraccion-api-ui-qa.md#mod-02-ingesta-pdf-y-extracción-ia) |
| — | 2026-11-12 | MOD-02 | Proveedor LLM abstracto vía config | [→](base-02-05-extraccion-api-ui-qa.md#mod-02-ingesta-pdf-y-extracción-ia) |
| — | 2026-11-12 | MOD-02 | OpenAI `gpt-4o-mini` como proveedor fijado | [→](base-02-05-extraccion-api-ui-qa.md#mod-02-ingesta-pdf-y-extracción-ia) |
| ADR-03-01 | 2026-11-12 | MOD-03 | DTOs con `cuit_emisor` y `monto_total` planos (listar el historial sin traer `datos_extraidos`) | [→](adr-03-01-dtos-con-cuit-y-monto-planos.md) |
| ADR-03-02 | 2026-11-12 | MOD-03 | `app` construida perezosamente con `__getattr__` (importarla desde tests no crea la BD real) | [→](adr-03-02-app-perezosa-con-getattr.md) |
| ADR-03-03 | 2026-11-12 | MOD-03 | Conexión SQLite con `threading.Lock` + `cerrar()` en lifespan (endpoints sync en threadpool) | [→](adr-03-03-sqlite-con-lock-y-cierre.md) |
| ADR-03-04 | 2026-11-12 | MOD-03 | Errores vía handlers de excepción (cuerpos `{"error": {...}}` exactos, sin wrapper `detail`) | [→](adr-03-04-errores-via-handlers.md) |
| ADR-03-05 | 2026-11-12 | MOD-03 | Escenario R4 probado con extractor stub (el mock no trae variante `FALTA_ORDEN_COMPRA`) | [→](adr-03-05-escenario-r4-extractor-stub.md) |
| ADR-03-06 | 2026-11-12 | MOD-03 | `reportlab` solo para el script `generar_ejemplos.py`, nunca en `src/` | [→](adr-03-06-reportlab-solo-para-ejemplos.md) |
| ADR-03-07 | 2026-11-12 | MOD-03 | Montos de `datos_extraidos` como número JSON (pydantic v2 serializa `Decimal` como string) | [→](adr-03-07-montos-como-numero-json.md) |
| ADR-03-08 | 2026-11-13 | MOD-03 | Desempate del historial por `rowid DESC` (en CI dos auditorías del mismo segundo devolvían orden indefinido) | [→](adr-03-08-desempate-historial-por-rowid.md) |
| — | 2026-11-12 | MOD-03 | `RECHAZADO` responde `200 OK` (resultado de negocio) | [→](base-02-05-extraccion-api-ui-qa.md#mod-03-api-rest-y-sqlite) |
| — | 2026-11-12 | MOD-03 | Estado `ERROR_EXTRACCION` solo en tabla | [→](base-02-05-extraccion-api-ui-qa.md#mod-03-api-rest-y-sqlite) |
| — | 2026-11-12 | MOD-03 | SQLite WAL + `check_same_thread=False` | [→](base-02-05-extraccion-api-ui-qa.md#mod-03-api-rest-y-sqlite) |
| — | 2026-11-12 | MOD-03 | PDFs de ejemplo generados por script con fechas relativas | [→](base-02-05-extraccion-api-ui-qa.md#mod-03-api-rest-y-sqlite) |
| — | 2026-11-12 | MOD-03 | Montos `Decimal` → REAL + JSON numérico 2 decimales | [→](base-02-05-extraccion-api-ui-qa.md#mod-03-api-rest-y-sqlite) |
| — | 2026-11-12 | MOD-03 | Latencia desglosada por etapa (IA / reglas) | [→](base-02-05-extraccion-api-ui-qa.md#mod-03-api-rest-y-sqlite) |
| — | 2026-11-12 | MOD-03 | SQLite efímero en deploy (free tier) | [→](base-02-05-extraccion-api-ui-qa.md#mod-03-api-rest-y-sqlite) |
| ADR-04-05 | 2026-11-12 | MOD-04 | Espejo de tipos ajustado al contrato real de la API verificado por HTTP (no al boceto del design) | [→](adr-04-05-espejo-de-tipos-contrato-real.md) |
| ADR-04-06 | 2026-11-12 | MOD-04 | `VITE_API_URL` vacío → base `/api/v1` vía proxy de Vite (sin CORS en dev; absoluta en deploy) | [→](adr-04-06-vite-api-url-y-proxy.md) |
| ADR-04-07 | 2026-11-12 | MOD-04 | Verificación visual diferida a Playwright de MOD-05 (en MOD-04 se verificó a nivel API/contrato) | [→](adr-04-07-verificacion-visual-diferida-playwright.md) |
| — | 2026-11-12 | MOD-04 | `fetch` nativo sin axios | [→](base-02-05-extraccion-api-ui-qa.md#mod-04-frontend-clean-architecture) |
| — | 2026-11-12 | MOD-04 | Sin router ni store global | [→](base-02-05-extraccion-api-ui-qa.md#mod-04-frontend-clean-architecture) |
| — | 2026-11-12 | MOD-04 | Visor con `iframe` (sin pdf.js) | [→](base-02-05-extraccion-api-ui-qa.md#mod-04-frontend-clean-architecture) |
| — | 2026-11-12 | MOD-04 | Ejemplos auditados bajando el PDF y re-enviándolo | [→](base-02-05-extraccion-api-ui-qa.md#mod-04-frontend-clean-architecture) |
| ADR-05-01 | 2026-11-12 | MOD-05 | El mock resuelve la fixture por identidad del ejemplo (E2E con R3/R4 sin `LLM_API_KEY`) | [→](adr-05-01-mock-por-identidad-del-ejemplo.md) |
| ADR-05-02 | 2026-11-12 | MOD-05 | Reset de la BD efímera dentro del comando del `webServer` (en `globalSetup` fallaba con EPERM) | [→](adr-05-02-reset-bd-en-webserver.md) |
| ADR-05-03 | 2026-11-12 | MOD-05 | El E2E no aserta el render interno del visor (Chromium headless no muestra PDFs en línea) | [→](adr-05-03-e2e-no-aserta-visor.md) |
| ADR-05-04 | 2026-11-12 | MOD-05 | k6 contra BD efímera `qa/artifacts/k6-sofredoc.db` (RN-5-05) | [→](adr-05-04-k6-contra-bd-efimera.md) |
| ADR-05-05 | 2026-11-12 | MOD-05 | Workflow único de verificación sin deploy automático (pytest → ruff → build → playwright → k6 smoke) | [→](adr-05-05-workflow-ci-sin-deploy.md) |
| ADR-05-06 | 2026-11-12 | MOD-05 | p95 de 449 ms a 50 VUs: cuello en el lock de SQLite, aceptado (migración a Postgres fuera de alcance) | [→](adr-05-06-cuello-de-botella-lock-sqlite.md) |
| ADR-05-07 | 2026-11-12 | MOD-05 | Estado "Auditando…" asertado con `page.route` (delay 800 ms), backend intacto | [→](adr-05-07-estado-de-carga-con-page-route.md) |
| ADR-05-08 | 2026-11-13 | MOD-05 | E2E extendido a 10 escenarios (fixture REMITO para R0, PDFs escaneado/11 páginas, errores de red/502 sin créditos) | [→](adr-05-08-e2e-10-escenarios-y-remito.md) |
| ADR-05-09 | 2026-11-13 | MOD-05 | Puertos exclusivos del E2E 8010/5175 + `reuseExistingServer: false` (no depende del estado de la máquina) | [→](adr-05-09-puertos-exclusivos-e2e.md) |
| ADR-05-10 | 2026-11-13 | MOD-05 | k6 funcional separado del de saturación (correctitud del contrato bajo carga, `SMOKE=1` para CI) | [→](adr-05-10-k6-funcional-separado.md) |
| — | 2026-11-12 | MOD-05 | Uso de `EXTRACTOR_MODE=mock` en pruebas k6 | [→](base-02-05-extraccion-api-ui-qa.md#mod-05-qa-playwright-y-k6) |
| — | 2026-11-12 | MOD-05 | `retries: 0` en Playwright | [→](base-02-05-extraccion-api-ui-qa.md#mod-05-qa-playwright-y-k6) |
| — | 2026-11-12 | MOD-05 | Clock fijo `2026-11-12` en fixtures unitarios | [→](base-02-05-extraccion-api-ui-qa.md#mod-05-qa-playwright-y-k6) |
| — | 2026-11-12 | MOD-05 | Gate de cobertura como parte del DoD | [→](base-02-05-extraccion-api-ui-qa.md#mod-05-qa-playwright-y-k6) |
| — | 2026-11-12 | MOD-05 | k6 smoke de 10 VUs para CI | [→](base-02-05-extraccion-api-ui-qa.md#mod-05-qa-playwright-y-k6) |
| — | 2026-11-12 | MOD-05 | Deploy de cierre en Render + Vercel | [→](base-02-05-extraccion-api-ui-qa.md#mod-05-qa-playwright-y-k6) |
