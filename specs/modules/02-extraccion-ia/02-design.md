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
        (esquema_para_llm(): SIN `impuestos` — el modelo no suma, ADR-02-12)
                                        │ (ValidationError o Σ items + impuestos ≠ total ± $1
                                        │  [gate = ecuación de R3, solo FACTURA] → 1 reintento reforzado)
                                        ▼
            FacturaExtraida validada (impuestos recalculado en Python desde detalle_impuestos)
                                        │ (ningún intento valida → EXTRACCION_FALLIDA ·
                                        │  ningún intento cuadra → sale el último validado y R3 decide)
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

> `FacturaExtraida`, `ItemFactura` e `ImpuestoDetalle` (ADR-02-12) están definidos en MOD-01 §2 y **no se duplican**. El único ajuste permitido aquí: `model_json_schema()` se exporta para alimentar el Structured Output (RN-2-03) — vía `esquema_para_llm()`, que retira los campos calculados en Python (`impuestos`, ADR-02-12) antes de enviarlo al proveedor.

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
# backend/src/infrastructure/llm/structured_extractor.py (esencia real, ADR-02-12)
def esquema_para_llm() -> dict:
    """JSON Schema de FacturaExtraida SIN los campos calculados en Python (`impuestos`)."""
    esquema = FacturaExtraida.model_json_schema()
    esquema["properties"].pop("impuestos", None)   # el modelo no suma: Python recalcula
    return esquema

def _consistente(factura: FacturaExtraida) -> bool:
    """Gate pre-reintento: la MISMA ecuación de R3 (calculo_total + TOLERANCIA). Solo FACTURA."""
    if factura.tipo_comprobante != "FACTURA":
        return True                                # en REMITO decide R0 antes de cualquier matemática
    return abs(calculo_total(factura) - factura.monto_total) <= TOLERANCIA

class LLMStructuredExtractor:
    def __init__(self, proveedor: str, modelo: str) -> None: ...

    def extraer(self, texto_pdf: str, nombre_archivo: str) -> ExtraccionResultado:
        esquema = esquema_para_llm()
        ultima_valida: tuple[FacturaExtraida, dict] | None = None
        for intento in (1, 2):                      # RN-2-03: máximo 1 reintento
            crudo = completar_con_esquema(
                system=SYSTEM_PROMPT,
                user=build_user_prompt(texto_pdf, nombre_archivo, intento=intento),
                esquema_json=esquema,
                temperatura=0,
            )
            try:
                factura = FacturaExtraida.model_validate(crudo)
            except ValidationError:
                continue                            # reintento sobre ValidationError
            if _consistente(factura):
                return ExtraccionResultado(factura=factura, json_crudo_ia=crudo)
            ultima_valida = (factura, crudo)        # cuadratura pendiente: reintenta
        if ultima_valida:                           # ningún intento cuadró → R3 decide (200 OK)
            factura, crudo = ultima_valida
            return ExtraccionResultado(factura=factura, json_crudo_ia=crudo)
        raise ExtraccionFallida(...)                # nunca validó → EXTRACCION_FALLIDA
```

### Prompt (esencia, archivo `prompt.py` — ADR-02-10/11/12)

- **System:** "Sos un extractor de datos de comprobantes fiscales argentinos (AFIP/ARCA): facturas y remitos. Devolvés EXCLUSIVAMENTE un JSON conforme al esquema. Copiás los valores **literales** del texto sin corregir, calcular ni redondear, dígito a dígito. Los montos van SIEMPRE como números JSON con punto decimal, sin `$` ni separadores de miles; la fecha va `YYYY-MM-DD`. **ANCLA:** primero extraés `letra_comprobante` del encabezado — define cómo leer los montos (A: ítems netos SIN IVA; B/C: importes finales con IVA incluido). `detalle_impuestos`: UNA entrada por cada línea de impuesto del pie, con el concepto literal y el monto de ESA línea sola (sin sumar; la suma la calcula el sistema); excluir SIEMPRE el informativo 'IVA Contenido (Ley 27.743)' y no duplicar un tributo que figure en una tabla de desglose y también en la línea agregada 'Importe Otros Tributos'. `numero_comprobante`: Punto de Venta (5 dígitos) + '-' + Comp. Nro (8 dígitos), p. ej. '00005-00019384'. `impuestos` no se pide: lo calcula el sistema. Obligatorios: items, fecha_emision, cuit_emisor, razon_social, monto_total y tipo_comprobante."
- **User:** nombre del archivo como pista contextual + texto del PDF (truncado a ~30.000 caracteres). En el reintento se refuerzan: campos obligatorios, verificación aritmética (Σ cantidad × precio + cada línea de `detalle_impuestos` == IMPORTE TOTAL ± $1), reglas por letra y no-duplicación del pie.

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
