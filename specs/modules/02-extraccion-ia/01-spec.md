# SPEC-02: Ingesta PDF y Extracción IA — Requisitos y Alcance

> **Audiencia:** Producto, Negocio, Revisor Técnico.
> **Estado:** Draft / Approved / In Progress / Completed

## 1. Problema de Negocio

Los comprobantes llegan como PDFs con texto no estructurado: CUITs con distintos formatos, tablas de ítems con layout variable, totales embebidos en texto libre. Transformar ese texto en datos auditables a mano es el cuello de botella del proceso administrativo.

Este módulo resuelve la transformación usando **IA únicamente como extracción** (Structured Outputs): el LLM convierte texto no estructurado en un esquema tipado de Pydantic (`FacturaExtraida`), pero **jamás decide** la validez del comprobante — eso lo hace el motor determinista (MOD-01). Además debe existir un **modo mock** determinista que permita probar y estresar todo el sistema sin consumir créditos de IA.

## 2. Objetivos

- [ ] Extraer texto de PDFs digitales (con capa de texto) usando `pypdf` en < 500 ms.
- [ ] Mapear el texto a `FacturaExtraida` mediante Structured Outputs con validación estricta de Pydantic (temperature 0).
- [ ] Modo `EXTRACTOR_MODE=mock` que devuelve una extracción fija de fixture, sin llamadas de red.
- [ ] Tasa de extracción exitosa ≥ 95% sobre los 3 PDFs de ejemplo del proyecto (medida manual/Día 4).
- [ ] Latencia p95 del extractor (con LLM real) < 8 s; registrada en métricas de auditoría.

## 3. Reglas de Negocio y Restricciones

- **RN-2-01:** Solo se aceptan archivos **PDF** de hasta **5 MB** (validación de extensión/MIME en MOD-03; este módulo asume bytes PDF válidos).
- **RN-2-02:** Si el PDF no tiene capa de texto (escaneo de imagen), el extractor **no inventa datos**: devuelve el error `PDF_SIN_TEXTO`. No hay OCR en el MVP.
- **RN-2-03:** La salida del LLM debe validar 100% contra el esquema `FacturaExtraida`; si tras **1 reintento** no valida, se propaga `EXTRACCION_FALLIDA` (nunca se acepta un objeto a medias).
- **RN-2-04:** El JSON crudo devuelto por el LLM se conserva para trazabilidad (inspector de JSON en el frontend, CU-03 del documento maestro).
- **RN-2-05:** El modo `mock` es determinista: ante la misma entrada devuelve siempre la misma salida de fixture y no consume créditos.
- **RN-2-06:** El extractor nunca ejecuta validaciones de negocio (eso es MOD-01): solo extrae datos literales del documento.
- **RN-2-07:** Límite de **10 páginas** por comprobante: pypdf concatena el texto de todas las páginas (tabla de ítems continuada); un PDF que supere las 10 páginas produce `PDF_INVALIDO` con mensaje específico de límite de páginas.
- **RN-2-08 (ADR-02-12):** El LLM extrae cada línea de impuesto del pie de forma literal en `detalle_impuestos` (`concepto` + `monto`, una entrada por línea); el campo `impuestos` **no viaja al LLM** — el sistema lo calcula en Python sumando el detalle con `Decimal` (la aritmética mental del modelo producía errores como 94.600 por 145.800). Exclusiones semánticas: los desgloses informativos de Ley 27.743 ('IVA Contenido') nunca se cargan, y un tributo que figure en una tabla de desglose Y también en la línea agregada 'Importe Otros Tributos' se carga UNA sola vez.
- **RN-2-09 (ADR-02-12):** La extracción con LLM se verifica aritméticamente en Python antes de devolverse — la MISMA ecuación de R3 (Σ(cantidad × precio) + impuestos == total ± $1.00, solo FACTURA; en REMITO decide R0). Si no cuadra, se reintenta 1 vez con refuerzo aritmético en el prompt (RN-2-03 conserva el tope de 2 llamadas); si ningún intento cuadra, se devuelve el último validado y el semáforo muestra R3 en rojo (RECHAZADO = 200 OK). Nunca se corrigen los datos extraídos.

## 4. Casos de Uso (Given-When-Then)

### CU-01: Extracción exitosa de factura digital
- **Given** un PDF digital de factura con capa de texto y hasta 5 MB
- **When** el sistema extrae el texto y lo procesa con Structured Outputs
- **Then** se obtiene una `FacturaExtraida` completa (tipo, letra, número con Punto de Venta, CUIT, razón social, fecha, OC opcional, ítems, detalle_impuestos, impuestos, total) y el JSON crudo queda disponible para trazabilidad.

### CU-02: PDF escaneado sin capa de texto
- **Given** un PDF generado a partir de imágenes (sin texto embebido)
- **When** `pypdf` devuelve texto vacío o casi vacío (< 20 caracteres significativos)
- **Then** el sistema responde con el error `PDF_SIN_TEXTO` sin llamar al LLM ni consumir créditos.

### CU-03: Respuesta del LLM que no valida contra el esquema
- **Given** un texto de PDF ambiguo que induce al LLM a omitir el campo `fecha_emision`
- **When** Pydantic rechaza la primera respuesta
- **Then** el sistema reintenta 1 vez (reforzando en el prompt los campos obligatorios) y si vuelve a fallar propaga `EXTRACCION_FALLIDA` con el detalle de los campos faltantes.

### CU-04: Modo mock para demos y pruebas de carga
- **Given** `EXTRACTOR_MODE=mock` en la configuración
- **When** cualquier fluido de auditoría solicita una extracción
- **Then** el `MockExtractor` devuelve la extracción del fixture en < 10 ms, sin red, y el flujo completo (reglas + API + frontend) queda demostrable sin IA.

### CU-05: Extracción aritméticamente inconsistente (ADR-02-12)
- **Given** un PDF cuyo LLM copia mal un monto del pie (caso real: 'IVA 10,5%: $ 46.200,00' devuelto como 46.000, sobre una capa de texto limpia)
- **When** Pydantic valida la respuesta pero Σ(cantidad × precio) + impuestos ≠ total ± $1.00
- **Then** el extractor reintenta 1 vez con verificación aritmética reforzada en el prompt; si el intento 2 cuadra se devuelve esa extracción; si tampoco cuadra se devuelve el último intento validado y el semáforo muestra R3 en rojo (`DISCREPANCIA_CONTABLE`, 200 OK) — nunca se corrigen los datos.

## 5. Fuera de Alcance (Out of Scope)

- OCR sobre imágenes escaneadas de baja calidad (explícito en el alcance del MVP).
- Multi-página con comprobantes mixtos (una factura + remito en el mismo archivo).
- Detección de fraude, duplicados o comparación contra facturas previas.
- Fine-tuning o RAG; solo prompt + Structured Outputs.
- Selección dinámica de proveedor de LLM en runtime (se fija por configuración).
