# DESIGN-02: Ingesta PDF y Extracción IA — Diseño Técnico

> **Audiencia:** Ingenieros de Software, Agentes de IA.
> **Patrón:** Clean Architecture (Monolito FastAPI + React).

## 1. Arquitectura de Componentes y Capas

```text
backend/src/
├── domain/ports/
│   ├── pdf_text_port.py           # PdfTextPort  (bytes → texto)
│   └── document_extractor_port.py # DocumentExtractorPort (texto → FacturaExtraida)
└── infrastructure/
    ├── pdf/pypdf_adapter.py       # PypdfTextExtractor
    └── llm/
        ├── client.py              # Cliente del proveedor de Structured Outputs
        ├── structured_extractor.py# LLMStructuredExtractor (adapter de DocumentExtractorPort)
        ├── mock_extractor.py      # MockExtractor (fixture determinista)
        └── prompt.py              # System/user prompt de extracción
```

### Pipeline de extracción

```text
bytes PDF ──► PypdfTextExtractor ──► texto plano
                                        │ (vacío <20 chars → PDF_SIN_TEXTO · >10 páginas → PDF_INVALIDO)
                                        ▼
              LLMStructuredExtractor: prompt + JSON Schema de FacturaExtraida
                                        │ (ValidationError → 1 reintento → EXTRACCION_FALLIDA)
                                        ▼
                              FacturaExtraida (validada por Pydantic) + json_crudo
```

## 2. Modelos de Datos y Esferas de Dominio

### Puertos (interfaces de dominio)

```python
# backend/src/domain/ports/pdf_text_port.py
from typing import Protocol

class PdfTextPort(Protocol):
    def extraer_texto(self, contenido: bytes) -> str: ...

# backend/src/domain/ports/document_extractor_port.py
from typing import Protocol
from src.domain.models import FacturaExtraida

class DocumentExtractorPort(Protocol):
    def extraer(self, texto_pdf: str, nombre_archivo: str) -> "ExtraccionResultado": ...
```

```python
# backend/src/domain/models.py (agregado de este módulo)
from typing import Optional
from pydantic import BaseModel

class ExtraccionResultado(BaseModel):
    factura: FacturaExtraida
    json_crudo_ia: Optional[dict] = None   # trazabilidad del output del LLM (None en mock ... o fixture)
```

> `FacturaExtraida` e `ItemFactura` están definidos en MOD-01 §2 y **no se duplican**. El único ajuste permitido aquí: `model_json_schema()` se exporta para alimentar el Structured Output (RN-2-03).

### Esquema de Base de Datos (SQLite)

No aplica (persistencia en MOD-03).

## 3. Contratos de API (HTTP / JSON)

No aplica (endpoint expuesto por MOD-03). Errores de dominio que este módulo propaga y MOD-03 mapea a HTTP:

| Error | Origen | HTTP (decisión en MOD-03) |
| :--- | :--- | :--- |
| `PDF_INVALIDO` | bytes no parseables por pypdf / PDF cifrado | 422 |
| `PDF_SIN_TEXTO` | texto extraído < 20 caracteres | 422 |
| `EXTRACCION_FALLIDA` | ValidationError tras 1 reintento / fallo del proveedor | 502 |

## 4. Librerías y Dependencias Elegidas

- `pypdf` (texto + metadatos). Fallback documentado: `pdfplumber` si los PDFs de ejemplo con tablas complejas requieren lectura por celdas.
- **Proveedor fijado: OpenAI `gpt-4o-mini`** con `response_format` JSON Schema (Structured Outputs nativo). Decisión confirmada por el product owner (2026-11-12); `client.py` encapsula el SDK (`openai>=1.40`) de modo que un cambio futuro de proveedor solo toque ese archivo.
- Sin frameworks de agentes: una sola llamada LLM por documento (simple, barato, trazable).

## 5. Detalle del Adapter LLM

```python
# backend/src/infrastructure/llm/structured_extractor.py (esqueleto)
import time
from pydantic import ValidationError
from src.domain.models import FacturaExtraida, ExtraccionResultado
from src.infrastructure.llm.prompt import SYSTEM_PROMPT, build_user_prompt
from src.infrastructure.llm.client import completar_con_esquema  # devuelve dict

class LLMStructuredExtractor:
    def __init__(self, proveedor: str, modelo: str) -> None: ...

    def extraer(self, texto_pdf: str, nombre_archivo: str) -> ExtraccionResultado:
        esquema = FacturaExtraida.model_json_schema()
        inicio = time.perf_counter()
        for intento in (1, 2):                      # RN-2-03: máximo 1 reintento
            crudo = completar_con_esquema(
                system=SYSTEM_PROMPT,
                user=build_user_prompt(texto_pdf, nombre_archivo, intento=intento),
                esquema_json=esquema,
                temperatura=0,
            )
            try:
                factura = FacturaExtraida.model_validate(crudo)
                return ExtraccionResultado(
                    factura=factura,
                    json_crudo_ia=crudo,
                )
            except ValidationError as e:
                ultimo_error = e
        raise ExtraccionFallida(str(ultimo_error))  # → EXTRACCION_FALLIDA
```

### Prompt (esencia, archivo `prompt.py`)

- **System:** "Sos un extractor de datos de comprobantes comerciales argentinos. Devolvés EXCLUSIVAMENTE un JSON conforme al esquema. Copiás los valores **literales** del texto sin corregir, calcular ni redondear. Los montos van como números con punto decimal. La fecha va `YYYY-MM-DD`. Si un campo no aparece en el texto, `null` salvo `items`, `fecha_emision`, `cuit_emisor`, `razon_social`, `monto_total`, `tipo_comprobante` que son obligatorios."
- **User:** el texto del PDF (truncado a ~30.000 caracteres) + el nombre del archivo como pista contextual.

### Modo mock (`mock_extractor.py`)

- Lee `backend/data/fixtures/extraccion-esperada.json` (una `FacturaExtraida` serializada válida, el caso feliz de ejemplo).
- Expone además variante `mock_rechazado` vía `MOCK_VARIANT` (opcional, default `aprobada`) para poder probar respuestas RECHAZADO en pruebas de carga.
- Registra latencia fija ~5 ms y `json_crudo_ia = fixture` (trazabilidad uniforme en la UI).

### Taxonomía de errores de extracción

| Excepción de infra | Código expuesto | Cuándo |
| :--- | :--- | :--- |
| `PdfInvalidoError` | `PDF_INVALIDO` | pypdf lanza al parsear; PDF cifrado sin password |
| `PdfSinTextoError` | `PDF_SIN_TEXTO` | texto < 20 caracteres significativos |
| `PdfDemasiadasPaginasError` | `PDF_INVALIDO` | PDF con más de 10 páginas (RN-2-07) |
| `ExtraccionFallidaError` | `EXTRACCION_FALLIDA` | ValidationError tras reintento / error del proveedor LLM |
