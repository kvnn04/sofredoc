# ADRs — Índice Maestro de Decisiones de Arquitectura

Catálogo navegable de **todas** las decisiones de arquitectura de SofreDoc Validator: **33 ADRs numerados** (registro formal) + **38 decisiones de base** (sin ID) = **71 registros**, cada uno con su fecha y texto original intacto.

> **Fuente única de verdad:** cada decisión vive en el §4 (ADR Log) del `04-verification.md` de su módulo de origen. Este índice **no duplica contenido**: cataloga y enlaza por ancla directa a cada ADR. Si editás un ADR, editá solo su §4 — el índice solo lleva el resumen de una línea.

---

## Cómo navegar

- **Por tema:** tablas de las 6 categorías más abajo, con link directo por ancla a cada ADR.
- **Por módulo:** el §4 completo de cada módulo — [MOD-00](modules/00-monolito-core/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log) · [MOD-01](modules/01-motor-reglas/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log) · [MOD-02](modules/02-extraccion-ia/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log) · [MOD-03](modules/03-api-sqlite/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log) · [MOD-04](modules/04-frontend/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log) · [MOD-05](modules/05-qa-testing/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log).
- **Para entrevista:** los 8 ADRs que más se citan, con pregunta típica y respuesta breve → [sección siguiente](#los-8-adrs-clave-para-la-entrevista).

---

## Los 8 ADRs clave para la entrevista

Mini-guion de 30 segundos por ADR: qué pregunta responde, qué contestar y dónde está la evidencia.

**1. ADR-02-12 — Impuestos calculado en Python y gate de consistencia** *(MOD-02 · 2026-11-14)*
- *Responde a:* "¿Cómo evitan que la IA alucine o erre montos?" / "¿Qué pasa si el LLM suma mal?"
- *Respuesta:* El LLM transcribe el pie del comprobante línea a línea (`detalle_impuestos`) y el campo `impuestos` lo recalcula Python con `Decimal`: el schema ya no le pide la suma al modelo. Antes de reintentar, un gate evalúa la misma ecuación de R3; si nada cuadra, sale el último intento válido y R3 rechaza (RECHAZADO = 200 OK, nunca se corrigen datos). Nació de un bug real: alícuotas mixtas sumadas "de memoria" ($94.600 por $145.800) — y en la verificación con LLM real el gate detectó un resbalón de copia de 46.000 por 46.200.
- *Link:* [`02-extraccion-ia/04-verification.md`](modules/02-extraccion-ia/04-verification.md#adr-02-12-impuestos-calculado-en-python-y-gate-de-consistencia)

**2. ADR-02-08 — Decimal del esquema colapsado a rama numérica en strict** *(MOD-02 · 2026-11-13)*
- *Responde a:* "¿Problemas reales con Structured Outputs?" / "¿Qué rompió el modo strict?"
- *Respuesta:* Pydantic serializa `Decimal` como `anyOf [number, string]`; con LLM real el proveedor elegía la rama string (montos es-AR tipo `'$200.000,00'`) y toda extracción caía en `EXTRACCION_FALLIDA`. Fix: colapsar ese anyOf a `{"type": "number"}` + prompt reforzado. Bug solo visible en modo `llm` — el mock lo escondía. Lección: el schema que viaja al proveedor es un contrato aparte y se testea contra el proveedor real.
- *Link:* [`02-extraccion-ia/04-verification.md`](modules/02-extraccion-ia/04-verification.md#adr-02-08-decimal-del-esquema-colapsado-a-rama-numérica-en-strict)

**3. ADR-02-10 — Semántica AFIP en el esquema y el prompt** *(MOD-02 · 2026-11-14)*
- *Responde a:* "¿Cómo validaron el sistema con documentos reales?"
- *Respuesta:* Primera Factura A real: el LLM casaba `impuestos` con la fila 'Importe Otros Tributos' ($0) porque el campo no tenía descripción → R3 rechazaba por $74.130 un comprobante correcto. Fix 100% semántico: descripciones AFIP campo por campo (viajan al JSON Schema strict) + reglas explícitas en el prompt. R3 intacta, fixture de regresión, verificación 4/4 con LLM real.
- *Link:* [`02-extraccion-ia/04-verification.md`](modules/02-extraccion-ia/04-verification.md#adr-02-10-semántica-afip-en-el-esquema-y-el-prompt)

**4. ADR-02-11 — Letra de comprobante y Transparencia Fiscal Ley 27.743** *(MOD-02 · 2026-11-14)*
- *Responde a:* "¿Qué particularidades fiscales argentinas modelaron?"
- *Respuesta:* En una Factura B real, el recuado 'IVA Contenido (Ley 27.743)' es informativo: ya está incluido en el total. El LLM lo sumaba como tributo adicional → discrepancia falsa. Fix: campo `letra_comprobante` que ancla el prompt por letra (A: netos + impuestos adicionados; B/C: importes finales con IVA incluido, `impuestos = 0` salvo percepciones). R3 intacta, verificación 5/5 con LLM real.
- *Link:* [`02-extraccion-ia/04-verification.md`](modules/02-extraccion-ia/04-verification.md#adr-02-11-letra-de-comprobante-y-transparencia-fiscal-ley-27743)

**5. ADR-03-08 — Desempate del historial por rowid DESC** *(MOD-03 · 2026-11-13)*
- *Responde a:* "Contá un bug real que hayas resuelto."
- *Respuesta:* En CI, el E2E insertaba dos auditorías en el mismo segundo (`creado_en` tiene precisión de segundos); el `ORDER BY creado_en DESC` sin desempate devolvía empates en orden indefinido y la UI mostraba como "más reciente" la auditoría equivocada. Fix: `creado_en DESC, rowid DESC` + test de integración que reproduce el empate de forma determinística. Detectado por el E2E en el runner de CI, no a mano.
- *Link:* [`03-api-sqlite/04-verification.md`](modules/03-api-sqlite/04-verification.md#adr-03-08-desempate-del-historial-por-rowid-desc)

**6. ADR-05-06 — Cuello de botella en el lock de SQLite a 50 VUs** *(MOD-05 · 2026-11-12)*
- *Responde a:* "¿Qué encontró tu prueba de carga?" / "¿Dónde está tu límite de escala?"
- *Respuesta:* p95 de 449 ms a 50 VUs (umbral 500 ms), 0.00% de error: el cuello es la conexión SQLite compartida con lock (serializa inserts/lecturas), no la extracción (< 10 ms). Documentado como limitación con camino de migración (Postgres/pool de conexiones), fuera de alcance del MVP. Complemento: ADR-05-10 separa la correctitud del contrato bajo carga de la saturación.
- *Link:* [`05-qa-testing/04-verification.md`](modules/05-qa-testing/04-verification.md#adr-05-06-cuello-de-botella-en-el-lock-de-sqlite-a-50-vus)

**7. Sin ID (MOD-03) — RECHAZADO responde 200 OK**
- *Responde a:* "¿Un RECHAZADO no debería ser un 4xx?"
- *Respuesta:* El rechazo es un **resultado de negocio correcto** del sistema: HTTP habla del contrato y el transporte; el body, del resultado. 4xx/5xx quedan reservados a fallos de contrato/infraestructura (413 `ARCHIVO_MUY_GRANDE`, 422 `PDF_INVALIDO`, 502 `EXTRACCION_FALLIDA`). Así el monitoreo nunca confunde rechazos legítimos con fallos del sistema.
- *Link:* [`03-api-sqlite/04-verification.md` §4](modules/03-api-sqlite/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

**8. Sin ID (MOD-00/01) — Clean Architecture + dominio puro + R0 de admisión**
- *Responde a:* "¿Por qué tanta arquitectura en un PoC?"
- *Respuesta:* El dominio es Python puro (prohibido importar FastAPI/SQLite/pypdf/SDK LLM): 100% de cobertura, cero I/O en tests unitarios, reloj y padrón inyectados por puertos (`ClockPort`, `PadrónPort`). Ese aislamiento es el que hace triviales los reemplazos futuros — persistencia real, padrón AFIP/ARCA, OCR: cada uno es un adaptador nuevo, no una cirugía. La regla de admisión R0 (un remito se rechaza sin evaluar R1–R5) es la única excepción declarada al "sin cortocircuito".
- *Links:* [`00-monolito-core/04-verification.md` §4](modules/00-monolito-core/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log) · [`01-motor-reglas/04-verification.md` §4](modules/01-motor-reglas/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

---

## Índice por categoría

### 1. Extracción IA

| ID | Fecha | Problema resuelto | Decisión clave | Módulo | Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| ADR-02-01 | 2026-11-12 | Dependencia del SDK declarada en el design pero ausente del archivo | `openai>=1.40` agregada a requirements.txt, aprobada por Kevin | MOD-02 | [→](modules/02-extraccion-ia/04-verification.md#adr-02-01-openai-agregada-a-requirementstxt) |
| ADR-02-03 | 2026-11-12 | El JSON Schema de Pydantic es rechazado por el modo strict del proveedor | `preparar_esquema_estricto()` limpia claves no soportadas y blinda `required`/`additionalProperties` | MOD-02 | [→](modules/02-extraccion-ia/04-verification.md#adr-02-03-esquema-estricto-con-preparar_esquema_estricto) |
| ADR-02-04 | 2026-11-12 | ¿Se reintenta un fallo del proveedor LLM? | Se tipifica y NO se reintenta: reintento solo sobre `ValidationError` | MOD-02 | [→](modules/02-extraccion-ia/04-verification.md#adr-02-04-fallo-del-proveedor-se-tipifica-y-no-se-reintenta) |
| ADR-02-05 | 2026-11-12 | La variante del mock no estaba en la tabla de configuración | `MOCK_VARIANT` como 12ª variable de config (default `aprobada`) | MOD-02 | [→](modules/02-extraccion-ia/04-verification.md#adr-02-05-mock_variant-como-variable-de-configuración) |
| ADR-02-07 | 2026-11-12 | El mock y los tests no deben exigir el SDK instalado | Import lazy del SDK + umbral determinista de 20 caracteres significativos | MOD-02 | [→](modules/02-extraccion-ia/04-verification.md#adr-02-07-sdk-importado-lazy-con-umbral-de-caracteres-significativos) |
| ADR-02-08 | 2026-11-13 | Con LLM real, `Decimal` generaba anyOf y el proveedor elegía la rama string → `EXTRACCION_FALLIDA` | Colapsar el anyOf a `{"type": "number"}` + prompt reforzado | MOD-02 | [→](modules/02-extraccion-ia/04-verification.md#adr-02-08-decimal-del-esquema-colapsado-a-rama-numérica-en-strict) |

### 2. Semántica fiscal

| ID | Fecha | Problema resuelto | Decisión clave | Módulo | Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| ADR-02-10 | 2026-11-14 | Factura A real con IVA discriminado daba falso positivo: el LLM casaba `impuestos` con 'Importe Otros Tributos' ($0) | Descripciones AFIP campo por campo en el schema + reglas explícitas de prompt + reintento reforzado | MOD-02 | [→](modules/02-extraccion-ia/04-verification.md#adr-02-10-semántica-afip-en-el-esquema-y-el-prompt) |
| ADR-02-11 | 2026-11-14 | Factura B real: el recuado de Transparencia Fiscal (Ley 27.743) se cargaba como tributo adicional | `letra_comprobante` + descripciones y prompt por letra; `impuestos = 0` en B/C salvo percepciones | MOD-02 | [→](modules/02-extraccion-ia/04-verification.md#adr-02-11-letra-de-comprobante-y-transparencia-fiscal-ley-27743) |
| ADR-02-12 | 2026-11-14 | Alícuotas mixtas sumadas "de memoria" por el LLM ($94.600 por $145.800) | `detalle_impuestos` línea a línea + `impuestos` recalculado en Python + gate de consistencia pre-reintento (ecuación compartida con R3) | MOD-02 | [→](modules/02-extraccion-ia/04-verification.md#adr-02-12-impuestos-calculado-en-python-y-gate-de-consistencia) |

### 3. Dominio, datos y arquitectura

| ID | Fecha | Problema resuelto | Decisión clave | Módulo | Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| ADR-02-02 | 2026-11-12 | Errores "de infra" no capturables desde application/presentation sin acoplarse a adaptadores | Excepciones puras en `domain/errors.py` con atributo `codigo` | MOD-02 | [→](modules/02-extraccion-ia/04-verification.md#adr-02-02-errores-de-extracción-en-el-dominio) |
| ADR-03-03 | 2026-11-12 | Endpoints sync en threadpool + conexión SQLite compartida | `threading.Lock` + `cerrar()` en lifespan | MOD-03 | [→](modules/03-api-sqlite/04-verification.md#adr-03-03-conexión-sqlite-con-threadinglock-y-cierre-en-lifespan) |
| ADR-03-08 | 2026-11-13 | Bug de CI: auditorías en el mismo segundo devolvían orden indefinido en el historial | Desempate por `rowid DESC` + test que reproduce el empate de forma determinística | MOD-03 | [→](modules/03-api-sqlite/04-verification.md#adr-03-08-desempate-del-historial-por-rowid-desc) |
| ADR-05-06 | 2026-11-12 | p95 de 449 ms a 50 VUs, cerca del umbral de 500 ms | Aceptado como observación: cuello identificado (lock de SQLite), migración a Postgres/pool fuera de alcance | MOD-05 | [→](modules/05-qa-testing/04-verification.md#adr-05-06-cuello-de-botella-en-el-lock-de-sqlite-a-50-vus) |

### 4. API y contratos

| ID | Fecha | Problema resuelto | Decisión clave | Módulo | Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| ADR-03-01 | 2026-11-12 | El historial necesita CUIT/monto sin traer `datos_extraidos` completo | `cuit_emisor` y `monto_total` planos en los DTOs (aditivo, no rompe contrato) | MOD-03 | [→](modules/03-api-sqlite/04-verification.md#adr-03-01-dtos-con-cuit_emisor-y-monto_total-planos) |
| ADR-03-02 | 2026-11-12 | Importar `src.main` desde tests creaba la BD real | `app` construida perezosamente vía `__getattr__` | MOD-03 | [→](modules/03-api-sqlite/04-verification.md#adr-03-02-app-construida-perezosamente-con-__getattr__) |
| ADR-03-04 | 2026-11-12 | El contrato exige `{"error": {...}}` sin el wrapper `detail` de FastAPI | Handlers de excepción con `ErrorHTTPTipado` mapeado por `codigo` | MOD-03 | [→](modules/03-api-sqlite/04-verification.md#adr-03-04-errores-vía-handlers-de-excepción) |
| ADR-03-07 | 2026-11-12 | pydantic v2 serializa `Decimal` como string en modo JSON | Conversor explícito: montos número con 2 decimales en JSON | MOD-03 | [→](modules/03-api-sqlite/04-verification.md#adr-03-07-montos-de-datos_extraidos-como-número-json) |
| ADR-04-05 | 2026-11-12 | Los DTOs reales de MOD-03 diferían del boceto de DESIGN-04 | Espejo de tipos ajustado al contrato real verificado por HTTP | MOD-04 | [→](modules/04-frontend/04-verification.md#adr-04-05-espejo-de-tipos-ajustado-al-contrato-real-de-la-api) |
| ADR-04-06 | 2026-11-12 | CORS y configuración de la URL base en desarrollo | `VITE_API_URL` vacío → base `/api/v1` vía proxy de Vite; absoluta en deploy | MOD-04 | [→](modules/04-frontend/04-verification.md#adr-04-06-vite_api_url-vacío-usa-el-proxy-de-vite) |

### 5. QA y CI

| ID | Fecha | Problema resuelto | Decisión clave | Módulo | Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| ADR-03-05 | 2026-11-12 | El mock no trae variante R4 (`FALTA_ORDEN_COMPRA`) | Extractor stub inyectado para probar el escenario a nivel API | MOD-03 | [→](modules/03-api-sqlite/04-verification.md#adr-03-05-escenario-r4-probado-con-extractor-stub) |
| ADR-03-06 | 2026-11-12 | Dependencia para generar los PDFs de ejemplo | `reportlab` solo en el script `generar_ejemplos.py`, nunca en `src/` | MOD-03 | [→](modules/03-api-sqlite/04-verification.md#adr-03-06-reportlab-solo-para-el-script-de-ejemplos) |
| ADR-04-07 | 2026-11-12 | Sin navegador headless disponible en MOD-04 | Verificación visual diferida a Playwright de MOD-05 (y cerrada ahí: 5/5 × 2 pasadas) | MOD-04 | [→](modules/04-frontend/04-verification.md#adr-04-07-verificación-visual-diferida-a-playwright-de-mod-05) |
| ADR-05-01 | 2026-11-12 | E2E sin `LLM_API_KEY` no podía ejercitar R3/R4 | El mock resuelve fixture por identidad del ejemplo (matriz de verdad reproducible) | MOD-05 | [→](modules/05-qa-testing/04-verification.md#adr-05-01-mock-resuelve-fixture-por-identidad-del-ejemplo) |
| ADR-05-02 | 2026-11-12 | Borrar la BD en `globalSetup` fallaba con EPERM (archivo abierto por uvicorn) | Reset dentro del comando del `webServer` (`qa/e2e/reset-db.mjs`) | MOD-05 | [→](modules/05-qa-testing/04-verification.md#adr-05-02-reset-de-bd-efímera-dentro-del-comando-del-webserver) |
| ADR-05-03 | 2026-11-12 | Chromium headless no renderiza PDFs en línea | El E2E no aserta el visor de PDF (limitación del navegador, no del producto) | MOD-05 | [→](modules/05-qa-testing/04-verification.md#adr-05-03-el-e2e-no-aserta-el-render-interno-del-visor) |
| ADR-05-04 | 2026-11-12 | Ningún test de carga debe tocar la BD real (RN-5-05) | k6 corre contra BD efímera `qa/artifacts/k6-sofredoc.db` | MOD-05 | [→](modules/05-qa-testing/04-verification.md#adr-05-04-k6-corre-contra-bd-efímera-en-artifacts) |
| ADR-05-07 | 2026-11-12 | La auditoría mock responde < 10 ms: estado de carga inasertable sin flakes | Amplificar latencia con `page.route` (delay 800 ms), backend intacto | MOD-05 | [→](modules/05-qa-testing/04-verification.md#adr-05-07-estado-de-carga-asertado-con-page-route) |
| ADR-05-08 | 2026-11-13 | Pedidos ≥ 5 casos E2E nuevos | 10 escenarios + fixture REMITO + 2 PDFs fixture commiteados (escaneado / 11 páginas) | MOD-05 | [→](modules/05-qa-testing/04-verification.md#adr-05-08-e2e-extendido-a-10-escenarios-con-fixture-remito) |
| ADR-05-09 | 2026-11-13 | El E2E reutilizaba el backend manual (modo `llm`): matriz mock no aplicaba + créditos gastados | Puertos exclusivos :8010/:5175 + `reuseExistingServer: false` + `VITE_PROXY_TARGET` | MOD-05 | [→](modules/05-qa-testing/04-verification.md#adr-05-09-puertos-exclusivos-del-e2e-8010-y-5175) |
| ADR-05-10 | 2026-11-13 | El smoke de estrés solo mide códigos HTTP: un 200 con JSON malformado pasaría | k6 funcional separado (contrato / matriz / errores) con `SMOKE=1` para CI | MOD-05 | [→](modules/05-qa-testing/04-verification.md#adr-05-10-k6-funcional-separado-del-de-saturación) |

### 6. Operación y deploy

| ID | Fecha | Problema resuelto | Decisión clave | Módulo | Link |
| :--- | :--- | :--- | :--- | :--- | :--- |
| ADR-02-06 | 2026-11-12 | La fecha "hoy − 5 días" del fixture vence a los 60 días de R5 | Fixture con fecha estática `2026-11-07`; regenerar antes de la demo (≈ 2027-01-06) | MOD-02 | [→](modules/02-extraccion-ia/04-verification.md#adr-02-06-fixture-mock-con-fecha-estática) |
| ADR-02-09 | 2026-11-13 | p95 real de extracción 10.8 s > umbral de laboratorio (8 s) | Desvío aceptado y documentado: varianza del proveedor, no del código (motor < 10 ms) | MOD-02 | [→](modules/02-extraccion-ia/04-verification.md#adr-02-09-p95-de-extracción-real-y-desvío-de-latencia-aceptado) |
| ADR-05-05 | 2026-11-12 | ¿Deploy automático desde CI? | Workflow único de verificación (pytest → ruff → build → playwright → k6 smoke); deploy manual/scriptado | MOD-05 | [→](modules/05-qa-testing/04-verification.md#adr-05-05-workflow-único-de-verificación-sin-deploy-automático) |

---

## Decisiones de base (sin ID) — 38, resumidas por módulo

Decisiones fundacionales y de ajuste fino que anteceden a la numeración formal. Cada una conserva su fila completa (con motivo e impacto) en el §4 de su módulo — el link lleva al §4 entero.

### MOD-00 — Arquitectura Monolito & Core (3) — [§4](modules/00-monolito-core/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| Decisión |
| :--- |
| Migrar de `backend/app/` plano a Clean Architecture `backend/src/` |
| `pypdf` como parser PDF del MVP (fallback: `pdfplumber`) |
| Sin ORM: `sqlite3` stdlib |

### MOD-01 — Dominio y Motor de Reglas (12) — [§4](modules/01-motor-reglas/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| Decisión |
| :--- |
| `Decimal` en el dominio (no `float`) |
| Variante Módulo 11: dv=11→0, dv=10→9 |
| Evaluación de las 5 reglas siempre completa (sin cortocircuito) |
| `ClockPort` inyectable |
| Reloj de sistema en `America/Argentina/Buenos_Aires` |
| Regla de admisión R0 (remitos) |
| Dependencia `tzdata` con marcador `sys_platform == "win32"` |
| Sintaxis `X \| None` (PEP 604) + `collections.abc.Sequence` |
| `Proveedor` definido en `domain/ports/padron_port.py` |
| `digito_verificador_valido` retorna `False` si el formato es inválido |
| `detalles` tipado `dict[str, str]`; montos es-AR vía `formato_ars` |
| Fixture factory `factura(**overrides)` en `tests/unit/conftest.py` |

### MOD-02 — Ingesta PDF y Extracción IA (6) — [§4](modules/02-extraccion-ia/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| Decisión |
| :--- |
| `EXTRACTOR_MODE=mock` como default |
| `pypdf` MVP, `pdfplumber` como fallback |
| Máximo 1 reintento de LLM |
| `json_crudo_ia` persistido junto al resultado |
| Proveedor LLM abstracto vía config |
| OpenAI `gpt-4o-mini` como proveedor fijado |

### MOD-03 — API REST y SQLite (7) — [§4](modules/03-api-sqlite/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| Decisión |
| :--- |
| `RECHAZADO` responde `200 OK` (resultado de negocio) |
| Estado `ERROR_EXTRACCION` solo en tabla |
| SQLite WAL + `check_same_thread=False` |
| PDFs de ejemplo generados por script con fechas relativas |
| Montos `Decimal` → REAL + JSON numérico 2 decimales |
| Latencia desglosada por etapa (IA / reglas) |
| SQLite efímero en deploy (free tier) |

### MOD-04 — Frontend Clean Architecture (4) — [§4](modules/04-frontend/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| Decisión |
| :--- |
| `fetch` nativo sin axios |
| Sin router ni store global |
| Visor con `iframe` (sin pdf.js) |
| Ejemplos auditados bajando el PDF y re-enviándolo |

### MOD-05 — QA: Pytest, Playwright & k6 (6) — [§4](modules/05-qa-testing/04-verification.md#4-registro-de-decisiones-de-arquitectura-adr-log)

| Decisión |
| :--- |
| Uso de `EXTRACTOR_MODE=mock` en pruebas k6 |
| `retries: 0` en Playwright |
| Clock fijo `2026-11-12` en fixtures unitarios |
| Gate de cobertura como parte del DoD |
| k6 smoke de 10 VUs para CI |
| Deploy de cierre en Render + Vercel |

---

## Notas de mantenimiento

- **Gap de numeración:** la serie de MOD-04 continúa la numeración global del proyecto y arranca en **ADR-04-05**; no existen ADR-04-01..04. El DoD de MOD-05 los cita como "ADR-04-01..07" por rango completo.
- **Fuente de fechas:** `specs/PROGRESO.md` es la bitácora histórica de 18 sesiones y NO se reordena; es la referencia para auditar la fecha de cada decisión contra la sesión que la ejecutó.
- **ADR nuevo:** registrar la entrada en el §4 del módulo (formato `#### ADR-XX-YY: título` + bullets `Fecha` / `Decisión` / `Motivo / Contexto` / `Impacto`) y agregar la fila correspondiente en la categoría de este índice. Nada más.
- **Anclas:** los slugs siguen el algoritmo de GitHub (minúsculas; se eliminan `.` `:` `/` `(` `)` y otros símbolos; los espacios pasan a `-`; los acentos y `_` se conservan). Ejemplo: `#### ADR-02-11: ... Ley 27.743` → `#adr-02-11-letra-de-comprobante-y-transparencia-fiscal-ley-27743`.
- **Verificación de links:** los links internos de todos los `.md` del repo se validaron contra los slugs reales de los headings (script de escaneo, 0 rotos).
