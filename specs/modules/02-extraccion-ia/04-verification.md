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

> **Índice maestro:** todas las decisiones del proyecto —numeradas y de base— están catalogadas en el índice [`adr/README.md`](../../adr/README.md). El texto completo vive en [`specs/adr/`](../../adr/): los 12 ADRs numerados como archivos individuales y las decisiones de base en [`base-02-05-extraccion-api-ui-qa.md`](../../adr/base-02-05-extraccion-api-ui-qa.md). Esta sección queda como tabla resumen de navegación.

### Decisiones de base (sin ID)

Texto completo (motivo e impacto): [`base-02-05-extraccion-api-ui-qa.md` · MOD-02](../../adr/base-02-05-extraccion-api-ui-qa.md#mod-02-ingesta-pdf-y-extracción-ia)

| Fecha | Decisión |
| :--- | :--- |
| 2026-11-12 | `EXTRACTOR_MODE=mock` como default |
| 2026-11-12 | `pypdf` MVP, `pdfplumber` como fallback |
| 2026-11-12 | Máximo 1 reintento de LLM |
| 2026-11-12 | `json_crudo_ia` persistido junto al resultado |
| 2026-11-12 | Proveedor LLM abstracto vía config |
| 2026-11-12 | OpenAI `gpt-4o-mini` como proveedor fijado |

### Decisiones formales (numeradas)

| ID | Fecha | Decisión | Archivo |
| :--- | :--- | :--- | :--- |
| ADR-02-01 | 2026-11-12 | OpenAI agregada a requirements.txt | [→](../../adr/adr-02-01-openai-agregada-a-requirements.md) |
| ADR-02-02 | 2026-11-12 | Errores de extracción en el dominio | [→](../../adr/adr-02-02-errores-de-extraccion-en-el-dominio.md) |
| ADR-02-03 | 2026-11-12 | Esquema estricto con preparar_esquema_estricto | [→](../../adr/adr-02-03-esquema-estricto-structured-outputs.md) |
| ADR-02-04 | 2026-11-12 | Fallo del proveedor se tipifica y no se reintenta | [→](../../adr/adr-02-04-fallo-del-proveedor-no-se-reintenta.md) |
| ADR-02-05 | 2026-11-12 | MOCK_VARIANT como variable de configuración | [→](../../adr/adr-02-05-mock-variant-en-config.md) |
| ADR-02-06 | 2026-11-12 | Fixture mock con fecha estática | [→](../../adr/adr-02-06-fixture-mock-fecha-estatica.md) |
| ADR-02-07 | 2026-11-12 | SDK importado lazy con umbral de caracteres significativos | [→](../../adr/adr-02-07-sdk-importado-lazy.md) |
| ADR-02-08 | 2026-11-13 | Decimal del esquema colapsado a rama numérica en strict | [→](../../adr/adr-02-08-decimal-colapsado-a-rama-numerica.md) |
| ADR-02-09 | 2026-11-13 | p95 de extracción real y desvío de latencia aceptado | [→](../../adr/adr-02-09-p95-de-extraccion-desvio-aceptado.md) |
| ADR-02-10 | 2026-11-14 | Semántica AFIP en el esquema y el prompt | [→](../../adr/adr-02-10-semantica-afip-en-esquema-y-prompt.md) |
| ADR-02-11 | 2026-11-14 | Letra de comprobante y Transparencia Fiscal Ley 27.743 | [→](../../adr/adr-02-11-letra-de-comprobante-y-ley-27743.md) |
| ADR-02-12 | 2026-11-14 | Impuestos calculado en Python y gate de consistencia | [→](../../adr/adr-02-12-impuestos-calculado-en-python.md) |

## 5. Criterio de Aceptación Final (Definition of Done)

- [x] Todas las tareas de `03-tasks.md` están marcadas como `[x]`.
- [x] Todos los tests de Pytest pasan en verde (con LLM falsificado, sin red). — *Evidencia: 84 passed (suite completa); 32 del extractor; cobertura `infrastructure/pdf`+`infrastructure/llm` 100% (gate > 90%); `domain/` sigue 100% (gate MOD-01).*
- [x] Modo mock funciona end-to-end sin llamadas de red (verificable cortando la conexión). — *Evidencia: smoke de mock (1.74 ms) + `client.py` importa el SDK en perezoso; toda la suite corre offline.*
- [ ] Los 3 PDFs de ejemplo extraen correctamente con `EXTRACTOR_MODE=llm`. — *Pendiente por diseño: los PDFs de ejemplo se generan en MOD-03 (T-04); se ejecuta esta verificación al tenerlos (ver §2).*
- [x] Errores de extracción tipificados y documentados (`PDF_INVALIDO`, `PDF_SIN_TEXTO`, `EXTRACCION_FALLIDA`). — *`domain/errors.py` con atributo `codigo`; ADR-02-02.*
