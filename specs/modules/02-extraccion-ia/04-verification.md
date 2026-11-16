# VERIFICATION-02: Ingesta PDF y Extracción IA — Testing y Cierre

> **Audiencia:** QA, Lead Developer, CI/CD.

## 1. Pruebas Unitarias e Integración (Pytest)

```bash
# Tests del extractor (PDF + LLM + mock), con LLM falsificado
pytest backend/tests/unit/test_extractor.py -v

# Cobertura del módulo de infraestructura de extracción (sin SDK real)
pytest backend/tests/unit/test_extractor.py --cov=src/infrastructure/pdf --cov=src/infrastructure/llm --cov-report=term-missing
```

### Cobertura Mínima Requerida
- `infrastructure/pdf/` y `infrastructure/llm/` (adapters + factory): **> 90%** (la capa del SDK real se stuba).
- Casos obligatorios: PDF válido → texto; PDF corrupto → `PDF_INVALIDO`; PDF > 10 páginas → `PDF_INVALIDO`; PDF vacío de texto → `PDF_SIN_TEXTO`; LLM ok; LLM falla→reintento ok; LLM falla siempre → `EXTRACCION_FALLIDA`; mock determinista.

## 2. Verificación Manual con Documentos Reales

> **Nota de cierre (sesión MOD-02):** los ítems de esta sección dependen de los 3 PDFs de ejemplo, que se generan en MOD-03 (T-04, script reportlab) y de `LLM_API_KEY` configurada. Se ejecutan al cerrar MOD-03 / en la verificación cruzada; no bloquean el cierre del código de este módulo.

- [x] Con `EXTRACTOR_MODE=llm`: procesar los 3 PDFs de ejemplo (`factura-aprobada-001.pdf`, `factura-desvio-monto.pdf`, `factura-monto-alto-sin-oc.pdf`) y verificar que los campos extraídos coinciden con el documento (CUIT, razón social, fecha, ítems, total) — objetivo ≥ 95% de campos correctos. *(✅ 2026-11-13: matriz de verdad en verde — `ej-factura-aprobada` → APROBADO (CUIT 30-12345678-1, $384.000, OC-2026-0441), `ej-factura-desvio` → RECHAZADO R3, `ej-monto-alto-sin-oc` → RECHAZADO R4; 100% de campos correctos. Requirió ADR-02-08: los Decimal del esquema colapsan a rama numérica.)*
- [x] Subir un PDF escaneado (imagen) y confirmar el error `PDF_SIN_TEXTO` sin consumo de créditos. *(✅ 2026-11-13: PDF de 1 página solo-gráficos generado con reportlab → 422 `PDF_SIN_TEXTO` antes de la llamada LLM — cero créditos.)*
- [ ] Confirmar que el `json_crudo_ia` queda disponible para el inspector de la UI (CU-03 del documento maestro). *(API: ✓ verificado — `json_crudo_ia` poblado con montos como números. Falta la pasada visual de la UI con `EXTRACTOR_MODE=llm`, a cargo de Kevin: backend+frontend levantados.)*
- [x] Medir latencia de 5 extracciones reales consecutivas: p95 < 8 s (registrar valores en el ADR si hay desvíos). *(⚠️ 2026-11-13: medición extendida a 10 extracciones reales — muestras ms: 3113, 3103, 10423, 2578, 2958, 3619, 2661, 3078, 2447, 10798; mediana 3.103 ms ✓ pero p95 10.798 ms > 8 s. Desvío registrado en ADR-02-09.)*

## 3. Pruebas de Estrés y Rendimiento (k6)

No aplica en este módulo (el stub para k6 se ejercita desde MOD-05 usando `EXTRACTOR_MODE=mock`).

## 4. Registro de Decisiones de Arquitectura (ADR Log)

> **Índice maestro:** todas las decisiones del proyecto —numeradas y de base— están catalogadas y enlazadas por tema en [`specs/ADRs.md`](../../ADRs.md).

### Decisiones de base (sin ID)

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | `EXTRACTOR_MODE=mock` como default | Evitar créditos de IA en dev y pruebas k6; demo determinista. | Fixture `extraccion-esperada.json` obligatorio. |
| 2026-11-12 | `pypdf` MVP, `pdfplumber` como fallback | PoC prioriza liviandad; si los PDFs de ejemplo exigen lectura de tablas complejas, se cambia con ADR. | Posible reintento de extracción en Día 4. |
| 2026-11-12 | Máximo 1 reintento de LLM | Balance costo/latencia vs fiabilidad de esquema. | Fallos definitivos → `EXTRACCION_FALLIDA` (502). |
| 2026-11-12 | `json_crudo_ia` persistido junto al resultado | Trazabilidad exigida por CU-03 (inspector de JSON Pydantic). | Columna JSON nullable en SQLite (MOD-03). |
| 2026-11-12 | Proveedor LLM abstracto vía config | Evitar acoplamientos; Structured Outputs es un estándar disponible en varios proveedores. | `client.py` encapsula el SDK. |
| 2026-11-12 | OpenAI `gpt-4o-mini` como proveedor fijado | Confirmado por el product owner (key disponible); Structured Outputs nativo con JSON Schema. | Defaults de `LLM_PROVIDER`/`LLM_MODEL`; cambiar de proveedor solo toca `client.py`. |

### Decisiones formales (numeradas)

#### ADR-02-01: OpenAI agregada a requirements.txt

- **Fecha:** 2026-11-12
- **Decisión:** `openai>=1.40` agregada a `requirements.txt`
- **Motivo / Contexto:** El design la declara (§4) pero faltaba en el archivo; **aprobado por Kevin** vía pregunta en sesión.
- **Impacto:** Instalada 3.49.0 en el venv.

#### ADR-02-02: Errores de extracción en el dominio

- **Fecha:** 2026-11-12
- **Decisión:** errores de extracción en `domain/errors.py`
- **Motivo / Contexto:** El DESIGN los llamaba "de infra", pero `application/` y `presentation/` deben capturarlos sin importar adaptadores concretos. Excepciones puras con atributo `codigo`.
- **Impacto:** MOD-03 mapea `error.codigo` a HTTP (422/502).

#### ADR-02-03: Esquema estricto con preparar_esquema_estricto

- **Fecha:** 2026-11-12
- **Decisión:** `preparar_esquema_estricto()` en `client.py`
- **Motivo / Contexto:** El JSON Schema de Pydantic (`title`, `default`, `minItems`, `minLength`, `minimum`) es rechazado por el modo `strict` del proveedor; se quitan claves no soportadas, se exige `required` completo y `additionalProperties: false`. Las restricciones reales las aplica Pydantic (RN-2-03).
- **Impacto:** Esquema compatible con Structured Outputs; probado contra el esquema real.

#### ADR-02-04: Fallo del proveedor se tipifica y no se reintenta

- **Fecha:** 2026-11-12
- **Decisión:** fallo del proveedor se tipifica en `client.py` y NO se reintenta
- **Motivo / Contexto:** El reintento es exclusivamente sobre `ValidationError` (RN-2-03, CU-03); reintentar errores del proveedor duplicaría costo/latencia.
- **Impacto:** `ExtraccionFallidaError` inmediata al fallar la API.

#### ADR-02-05: MOCK_VARIANT como variable de configuración

- **Fecha:** 2026-11-12
- **Decisión:** `MOCK_VARIANT` como 12ª variable de config
- **Motivo / Contexto:** El DESIGN la menciona pero no estaba en la tabla §2 de DESIGN-00.
- **Impacto:** `config.py` + `.env.example`; default `aprobada`.

#### ADR-02-06: Fixture mock con fecha estática

- **Fecha:** 2026-11-12
- **Decisión:** fixture mock con fecha estática
- **Motivo / Contexto:** T-04 pide fecha "hoy − 5 días al momento de crear el fixture": se hornea `2026-11-07`. Riesgo conocido: tras 60 días (≈ 2027-01-06) la demo `aprobada` pasaría a RECHAZADO por R5 → regenerar fecha del fixture antes de esa demo.
- **Impacto:** Demo mock APROBADO válida hasta ≈ 2027-01-06.

#### ADR-02-07: SDK importado lazy con umbral de caracteres significativos

- **Fecha:** 2026-11-12
- **Decisión:** SDK importado en perezoso + umbral de "significativos"
- **Motivo / Contexto:** El modo mock y los tests no requieren `openai` instalado (client.py lo importa dentro de la función). "20 caracteres significativos" = caracteres sin espacios (`"".join(texto.split())`).
- **Impacto:** Mock cero-dependencia; umbral determinista.

#### ADR-02-08: Decimal del esquema colapsado a rama numérica en strict

- **Fecha:** 2026-11-13
- **Decisión:** `Decimal` del esquema colapsado a rama numérica en strict
- **Motivo / Contexto:** Con LLM real, Pydantic genera `anyOf [{number}, {string}]` para `Decimal` y el proveedor elegía la rama string → montos formateados es-AR (`'$200.000,00'`) que Pydantic rechaza → `EXTRACCION_FALLIDA` en 2 intentos (bug solo visible con `EXTRACTOR_MODE=llm`; el mock devuelve números limpios). Fix: `preparar_esquema_estricto` colapsa ese anyOf a `{"type": "number"}` + prompt reforzado ("montos números sin $ ni separadores"). No cambia contrato API ni reglas. 109 tests en verde; cobertura `infrastructure/llm` 100%.
- **Impacto:** Montos siempre números JSON; validación final sigue siendo Pydantic (RN-2-03).

#### ADR-02-09: p95 de extracción real y desvío de latencia aceptado

- **Fecha:** 2026-11-13
- **Decisión:** p95 de extracción real > 8 s (umbral no cumplido)
- **Motivo / Contexto:** 10 extracciones reales consecutivas: mediana 3.103 ms, pero outliers de 10.4 y 10.8 s (varianza de respuesta del proveedor `gpt-4o-mini` con Structured Outputs). PoC acepta el desvío: el umbral era de laboratorio; la latencia depende del proveedor, no del código (el motor de reglas sigue en < 10 ms). No cambia contrato API ni reglas de negocio.
- **Impacto:** p95 real ≈ 10.8 s — documentado; si la PoC lo exige, evaluar `gpt-4o` / timeout en el cliente (fuera de alcance MVP).

#### ADR-02-10: Semántica AFIP en el esquema y el prompt

- **Fecha:** 2026-11-14
- **Decisión:** semántica AFIP en el esquema y el prompt — Factura A con IVA discriminado
- **Motivo / Contexto:** Falso positivo con LLM real (reportado por Kevin con una Factura A real: neto $353.000, IVA 21% $74.130, 'Importe Otros Tributos' $0, total $427.130): el LLM devolvía `impuestos = 0` — el campo no tenía descripción y el prompt decía "impuestos faltante es 0", así que el modelo casaba el campo con la fila 'Importe Otros Tributos' → R3 rechazaba DISCREPANCIA_CONTABLE por $74.130. Fix solo de extracción (R3 intacta): `Field(description=...)` AFIP en `impuestos`, `items[].subtotal`, `items[].precio_unitario` y `monto_total` (las description viajan al JSON Schema strict — verificado con test) + SYSTEM_PROMPT con reglas explícitas (subtotales/precios netos vs 'Subtotal c/IVA'; impuestos = suma de TODOS los impuestos discriminados al pie; solo 0 en Factura B/C) + reintento reforzado. Fixture `data/fixtures/extraccion-factura-a-iva.json` (solo JSON sintético, decisión de Kevin; el PDF real queda fuera del repo) + 4 tests nuevos. Verificación con LLM real: **4/4 casos** (Factura A → APROBADO en intento 1; matriz de verdad intacta); 115 tests en verde (99.59%), ruff verde.
- **Impacto:** La IA sigue sin decidir (RN-2-06): solo se aclara qué campo es cuál; la matemática sigue en R3 con ± $1.00. El mock es inmune (fixtures estáticas) — este bug solo era visible en modo `llm`.

#### ADR-02-11: Letra de comprobante y Transparencia Fiscal Ley 27.743

- **Fecha:** 2026-11-14
- **Decisión:** letra del comprobante + Regla de Transparencia Fiscal (Ley 27.743) en B/C
- **Motivo / Contexto:** Segundo falso positivo con LLM real (Factura B real: ítems $340.000 + $185.000 + $95.000 = $620.000 con IVA incluido, total $620.000, recuado informativo 'IVA Contenido (Ley 27.743): $107.603,31'): el LLM cargaba `impuestos = 107603.31` desde ese dato informativo → R3 calculaba 620.000 + 107.603,31 ≠ 620.000 → DISCREPANCIA_CONTABLE. El recuado de Transparencia Fiscal es un desglose informativo YA INCLUIDO en el total (no se adiciona). Fix solo de extracción (R3 intacta): campo opcional `letra_comprobante` (str | null, patrón string | null probado en strict; ancla la regla por letra) + descripciones reescritas por letra (A: netos + impuestos = impuestos discriminados adicionados; B/C: importes finales con IVA incluido, `impuestos = 0` salvo percepciones/tributos adicionados) + regla explícita de NO cargar 'IVA Contenido' / 'Otros Impuestos Nacionales Indirectos' (Ley 27.743) + SYSTEM_PROMPT reestructurado por letra (ancla primero) + reintento reforzado. Fixture `extraccion-factura-b-transparencia.json` + 4 tests (letra B, impuestos 0, R3 verde, motor APROBADO con OC — total > $500.000 exige OC y la trae). Verificación con LLM real: **5/5 casos** (Factura B → APROBADO intento 1 con `letra=B, impuestos=0`; Factura A re-verificada como regresión → APROBADO con `letra=A, impuestos=74130`; matriz intacta). 119 tests en verde (99.59%), ruff verde, build frontend ✓ (espejo `types.ts` con `letra_comprobante`).
- **Impacto:** Invariante R3 intacto: `impuestos` = solo tributos que se adicionan a los subtotales. La letra es ancla de extracción + trazabilidad en el JSON inspector; ninguna regla la consume.

#### ADR-02-12: Impuestos calculado en Python y gate de consistencia

- **Fecha:** 2026-11-14
- **Decisión:** `detalle_impuestos` línea a línea + `impuestos` calculado en Python + gate de consistencia pre-reintento
- **Motivo / Contexto:** Tercer falso positivo con LLM real (Factura A real con alícuotas mixtas: neto $800.000 — $360.000 al 21% + $440.000 al 10,5% —, IVA 21% $75.600, IVA 10,5% $46.200, Percepción IIBB ARBA 3% $24.000, total $945.800): el schema le pedía un único escalar `impuestos` y el modelo sumaba las 3 líneas **de memoria** → devolvió 94.600 (error aritmético de $51.200) → R3 rechazaba. Además `numero_comprobante` salía '00019384' sin el Punto de Venta. **Decisión preguntada a Kevin (5/5 recomendados):** (1) el recálculo vive en el dominio, (2) `impuestos` sale del schema del LLM, (3) fixtures mock intactas + fixture nueva, (4) `numero` solo semántica (sin normalizar en código), (5) verificación con LLM real. Implementación: modelo `ImpuestoDetalle {concepto, monto}` + `FacturaExtraida.detalle_impuestos: list[ImpuestoDetalle]` (una entrada por línea, extraída literal) + `model_validator` que recalcula `impuestos = Σ montos` en Python/Decimal cuando el detalle trae líneas (retrocompat: fixtures mock sin el campo conservan su literal) + `numero_comprobante` con description 'PPPPP-NNNNNNNN' (ej. '00005-00019384') + `esquema_para_llm()` en el extractor retira `impuestos` del JSON Schema (el modelo ya no puede errar la suma; trazabilidad línea a línea en el JSON crudo) + reglas de prompt: copiar dígito a dígito, excluir Ley 27.743 y **no duplicar** un tributo que figure en una tabla de desglose ('DETALLE DE OTROS TRIBUTOS / PERCEPCIONES') y también en la línea agregada 'Importe Otros Tributos' del pie (son EL MISMO monto). **Gate de consistencia pre-reintento (extensión de RN-2-03, aprobada por Kevin):** el extractor evalúa la MISMA ecuación de R3 vía nuevo helper de dominio `calculo_total()` (fuente única con `TOLERANCIA`, solo FACTURA — en REMITO decide R0); si el intento no cuadra (Σ items + impuestos ≠ total ± $1) reintenta con verificación aritmética reforzada; si ningún intento cuadra, sale el último validado y R3 decide (RECHAZADO = 200 OK, nunca se corrigen datos). Fixture `extraccion-factura-a-mixta.json` (datos reales del comprobante; fecha estática 2026-11-14, caducidad R5 ≈ 2027-01-13) + 7 tests nuevos (5 de dominio/motor + 2 de esquema) + 3 del gate (reintento por inconsistencia, ambos intentos inconsistentes → R3, REMITO immune). Verificación con LLM real (4 corridas ad-hoc): mixta real → intento 1 inconsistente (el gate detectó un resbalón de copia 46.000 por 46.200) → **intento 2 → `impuestos = 145.800`, `numero = '00005-00019384'`, R1–R5 OK → APROBADO**; matriz intacta (aprobada → APROBADO; desvío genuino → RECHAZADO R3 consumiendo su reintento; monto-alto → RECHAZADO R4). 129 tests en verde (99.61%), ruff verde, build frontend ✓ (espejo `types.ts` con `ImpuestoDetalle`).
- **Impacto:** Contrato `datos_extraidos` extendido de forma aditiva (`detalle_impuestos`, campo nuevo dentro del JSON) — aprobado por Kevin; sin cambios de DDL ni de reglas (R3 intacta, ahora con la ecuación compartida en `calculo_total`). `json_crudo_ia` deja de incluir `impuestos` (el campo es derivado; la trazabilidad del pie queda en `detalle_impuestos`). Costo real: una extracción inconsistente puede consumir su 2º intento (+1 llamada) — aceptado; RN-2-03 conserva el tope de 2 llamadas.

## 5. Criterio de Aceptación Final (Definition of Done)

- [x] Todas las tareas de `03-tasks.md` están marcadas como `[x]`.
- [x] Todos los tests de Pytest pasan en verde (con LLM falsificado, sin red). — *Evidencia: 84 passed (suite completa); 32 del extractor; cobertura `infrastructure/pdf`+`infrastructure/llm` 100% (gate > 90%); `domain/` sigue 100% (gate MOD-01).*
- [x] Modo mock funciona end-to-end sin llamadas de red (verificable cortando la conexión). — *Evidencia: smoke de mock (1.74 ms) + `client.py` importa el SDK en perezoso; toda la suite corre offline.*
- [ ] Los 3 PDFs de ejemplo extraen correctamente con `EXTRACTOR_MODE=llm`. — *Pendiente por diseño: los PDFs de ejemplo se generan en MOD-03 (T-04); se ejecuta esta verificación al tenerlos (ver §2).*
- [x] Errores de extracción tipificados y documentados (`PDF_INVALIDO`, `PDF_SIN_TEXTO`, `EXTRACCION_FALLIDA`). — *`domain/errors.py` con atributo `codigo`; ADR-02-02.*
