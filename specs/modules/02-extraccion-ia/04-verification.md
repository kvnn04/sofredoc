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

- [ ] Con `EXTRACTOR_MODE=llm`: procesar los 3 PDFs de ejemplo (`factura-aprobada-001.pdf`, `factura-desvio-monto.pdf`, `factura-monto-alto-sin-oc.pdf`) y verificar que los campos extraídos coinciden con el documento (CUIT, razón social, fecha, ítems, total) — objetivo ≥ 95% de campos correctos. *(Pendiente: requiere MOD-03 T-04.)*
- [ ] Subir un PDF escaneado (imagen) y confirmar el error `PDF_SIN_TEXTO` sin consumo de créditos. *(La regla está cubierta por unit tests con PDF sin capa de texto; falta la prueba manual.)*
- [ ] Confirmar que el `json_crudo_ia` queda disponible para el inspector de la UI (CU-03 del documento maestro). *(Pendiente: la UI llega en MOD-04.)*
- [ ] Medir latencia de 5 extracciones reales consecutivas: p95 < 8 s (registrar valores en el ADR si hay desvíos). *(Pendiente: requiere llamadas reales; se registra costo en bitácora.)*

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
| 2026-11-12 | ADR-02-01: `openai>=1.40` agregada a `requirements.txt` | El design la declara (§4) pero faltaba en el archivo; **aprobado por Kevin** vía pregunta en sesión. | Instalada 3.49.0 en el venv. |
| 2026-11-12 | ADR-02-02: errores de extracción en `domain/errors.py` | El DESIGN los llamaba "de infra", pero `application/` y `presentation/` deben capturarlos sin importar adaptadores concretos. Excepciones puras con atributo `codigo`. | MOD-03 mapea `error.codigo` a HTTP (422/502). |
| 2026-11-12 | ADR-02-03: `preparar_esquema_estricto()` en `client.py` | El JSON Schema de Pydantic (`title`, `default`, `minItems`, `minLength`, `minimum`) es rechazado por el modo `strict` del proveedor; se quitan claves no soportadas, se exige `required` completo y `additionalProperties: false`. Las restricciones reales las aplica Pydantic (RN-2-03). | Esquema compatible con Structured Outputs; probado contra el esquema real. |
| 2026-11-12 | ADR-02-04: fallo del proveedor se tipifica en `client.py` y NO se reintenta | El reintento es exclusivamente sobre `ValidationError` (RN-2-03, CU-03); reintentar errores del proveedor duplicaría costo/latencia. | `ExtraccionFallidaError` inmediata al fallar la API. |
| 2026-11-12 | ADR-02-05: `MOCK_VARIANT` como 12ª variable de config | El DESIGN la menciona pero no estaba en la tabla §2 de DESIGN-00. | `config.py` + `.env.example`; default `aprobada`. |
| 2026-11-12 | ADR-02-06: fixture mock con fecha estática | T-04 pide fecha "hoy − 5 días al momento de crear el fixture": se hornea `2026-11-07`. Riesgo conocido: tras 60 días (≈ 2027-01-06) la demo `aprobada` pasaría a RECHAZADO por R5 → regenerar fecha del fixture antes de esa demo. | Demo mock APROBADO válida hasta ≈ 2027-01-06. |
| 2026-11-12 | ADR-02-07: SDK importado en perezoso + umbral de "significativos" | El modo mock y los tests no requieren `openai` instalado (client.py lo importa dentro de la función). "20 caracteres significativos" = caracteres sin espacios (`"".join(texto.split())`). | Mock cero-dependencia; umbral determinista. |

## 5. Criterio de Aceptación Final (Definition of Done)

- [x] Todas las tareas de `03-tasks.md` están marcadas como `[x]`.
- [x] Todos los tests de Pytest pasan en verde (con LLM falsificado, sin red). — *Evidencia: 84 passed (suite completa); 32 del extractor; cobertura `infrastructure/pdf`+`infrastructure/llm` 100% (gate > 90%); `domain/` sigue 100% (gate MOD-01).*
- [x] Modo mock funciona end-to-end sin llamadas de red (verificable cortando la conexión). — *Evidencia: smoke de mock (1.74 ms) + `client.py` importa el SDK en perezoso; toda la suite corre offline.*
- [ ] Los 3 PDFs de ejemplo extraen correctamente con `EXTRACTOR_MODE=llm`. — *Pendiente por diseño: los PDFs de ejemplo se generan en MOD-03 (T-04); se ejecuta esta verificación al tenerlos (ver §2).*
- [x] Errores de extracción tipificados y documentados (`PDF_INVALIDO`, `PDF_SIN_TEXTO`, `EXTRACCION_FALLIDA`). — *`domain/errors.py` con atributo `codigo`; ADR-02-02.*
