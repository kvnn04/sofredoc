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

- [ ] Con `EXTRACTOR_MODE=llm`: procesar los 3 PDFs de ejemplo (`factura-aprobada-001.pdf`, `factura-desvio-monto.pdf`, `factura-monto-alto-sin-oc.pdf`) y verificar que los campos extraídos coinciden con el documento (CUIT, razón social, fecha, ítems, total) — objetivo ≥ 95% de campos correctos.
- [ ] Subir un PDF escaneado (imagen) y confirmar el error `PDF_SIN_TEXTO` sin consumo de créditos.
- [ ] Confirmar que el `json_crudo_ia` queda disponible para el inspector de la UI (CU-03 del documento maestro).
- [ ] Medir latencia de 5 extracciones reales consecutivas: p95 < 8 s (registrar valores en el ADR si hay desvíos).

## 3. Pruebas de Estrés y Rendimiento (k6)

No aplica en este módulo (el stub para k6 se ejercita desde MOD-05 usando `EXTRACTOR_MODE=mock`).

## 4. Registro de Decisiones de Arquitectura (ADR Log)

| Fecha | Decisión | Motivo / Contexto | Impacto |
| :--- | :--- | :--- | :--- |
| 2026-11-12 | `EXTRACTOR_MODE=mock` como default | Evitar créditos de IA en dev y pruebas k6; demo determinista. | Fixture `extraccion-esperada.json` obligatorio. |
| 2026-11-12 | `pypdf` MVP, `pdfplumber` como fallback | PoC prioriza liviandad; si los PDFs de ejemplo exigen lectura de tablas complejas, se cambia con ADR. | Posible reintento de extracción en Día 4. |
| 2026-11-12 | Máximo 1 reintento de LLM | Balance costo/latencia vs fiabilidad de esquema. | Fallos definitivos → `EXTRACCION_FALLIDA` (502). |
| 2026-11-12 | `json_crudo_ia` persistido junto al resultado | Trazabilidad exigida por CU-03 (inspector de JSON Pydantic). | Columna JSON nullable en SQLite (MOD-03). |
| 2026-11-12 | Proveedor LLM abstracto vía config | Evitar acoplamientos; Structured Outputs es un estándar disponible en varios proveedores. | `client.py` encapsula el SDK. |
| 2026-11-12 | OpenAI `gpt-4o-mini` como proveedor fijado | Confirmado por el product owner (key disponible); Structured Outputs nativo con JSON Schema. | Defaults de `LLM_PROVIDER`/`LLM_MODEL`; cambiar de proveedor solo toca `client.py`. |

## 5. Criterio de Aceptación Final (Definition of Done)

- [ ] Todas las tareas de `03-tasks.md` están marcadas como `[x]`.
- [ ] Todos los tests de Pytest pasan en verde (con LLM falsificado, sin red).
- [ ] Modo mock funciona end-to-end sin llamadas de red (verificable cortando la conexión).
- [ ] Los 3 PDFs de ejemplo extraen correctamente con `EXTRACTOR_MODE=llm`.
- [ ] Errores de extracción tipificados y documentados (`PDF_INVALIDO`, `PDF_SIN_TEXTO`, `EXTRACCION_FALLIDA`).
