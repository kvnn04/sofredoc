# TASKS-02: Ingesta PDF y Extracción IA — Plan de Ejecución

> **Instrucción para la IA:** Ejecutar las tareas en orden estricto de dependencias. Tras completar cada tarea, marcar la casilla con `[x]` y asegurar que las pruebas unitarias sigan pasando.

## Fase 1: Lectura de PDF (Infraestructura)

- [ ] **T-01:** Definir el puerto `PdfTextPort` en `backend/src/domain/ports/pdf_text_port.py`.
- [ ] **T-02:** Implementar `PypdfTextExtractor` en `backend/src/infrastructure/pdf/pypdf_adapter.py`: extrae texto de todas las páginas, concatena, lanza `PdfInvalidoError` si no parsea o está cifrado, `PdfDemasiadasPaginasError` si supera 10 páginas, y `PdfSinTextoError` si el texto tiene < 20 caracteres significativos.

## Fase 2: Puerto de Extracción y Modo Mock

- [ ] **T-03:** Definir `DocumentExtractorPort` y agregar `ExtraccionResultado` a `backend/src/domain/models.py` (reutilizando `FacturaExtraida` de MOD-01, sin duplicar).
- [ ] **T-04:** Crear `backend/data/fixtures/extraccion-esperada.json` (caso feliz: CUIT `30-12345678-1`, ítems consistentes, fecha relativa generada a "hoy − 5 días" al momento de crear el fixture) y su variante `mock_rechazado` (desvío de monto > $1.00 para disparar R3).
- [ ] **T-05:** Implementar `MockExtractor` en `backend/src/infrastructure/llm/mock_extractor.py`: determinista, < 10 ms, selecciona fixture por `MOCK_VARIANT` (default `aprobada`).

## Fase 3: Extracción con LLM (Structured Outputs)

- [ ] **T-06:** Implementar `backend/src/infrastructure/llm/client.py`: envuelve el SDK del proveedor configurado (`LLM_PROVIDER`, `LLM_MODEL`, `LLM_API_KEY`) y fuerza Structured Outputs con el JSON Schema de `FacturaExtraida` (temperature 0).
- [ ] **T-07:** Escribir `backend/src/infrastructure/llm/prompt.py` con `SYSTEM_PROMPT` y `build_user_prompt()` según `02-design.md` §5 (valores literales, no calcular ni corregir; campos obligatorios explícitos).
- [ ] **T-08:** Implementar `LLMStructuredExtractor` con 1 reintento sobre ValidationError, logging de latencia y conservación del `json_crudo_ia` (RN-2-03 / RN-2-04).
- [ ] **T-09:** Implementar la fábrica de extractor en `backend/src/infrastructure/llm/factory.py`: devuelve `MockExtractor` si `EXTRACTOR_MODE=mock`, `LLMStructuredExtractor` si `llm` (error de arranque claro si `llm` sin `LLM_API_KEY`).

## Fase 4: Tests Unitarios

- [ ] **T-10:** Test de `PypdfTextExtractor` con fixture PDF mínimo en `backend/tests/fixtures/` (PDF de 1 página generado en test con `fpdf2`-free approach o PDF binario embebido): ok, no-parseable → `PdfInvalidoError`, sin texto → `PdfSinTextoError`.
- [ ] **T-11:** Test de `MockExtractor`: determinismo (dos llamadas → igual resultado), variantes `aprobada`/`rechazado` válidas contra el esquema.
- [ ] **T-12:** Test de `LLMStructuredExtractor` con cliente LLM **falsificado** (stub que devuelve dicts): respuesta válida ok; respuesta inválida en 1er intento y válida en el 2do → ok con reintento; inválida siempre → `ExtraccionFallidaError`; verificar que `json_crudo_ia` conserva el output crudo.
- [ ] **T-13:** Test de `factory.py`: selección por `EXTRACTOR_MODE` y error claro si `llm` sin API key.
