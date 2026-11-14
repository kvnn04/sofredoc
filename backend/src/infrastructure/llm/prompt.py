"""Prompts de extracción con Structured Outputs (DESIGN-02 §5).

La IA solo extrae (RN-2-06): copia valores literales del texto sin corregir,
calcular ni redondear. La validación final es de Pydantic, no del prompt.
"""

SYSTEM_PROMPT = (
    "Sos un extractor de datos de comprobantes fiscales argentinos (AFIP/ARCA): "
    "facturas y remitos. Devolvés EXCLUSIVAMENTE un JSON conforme al esquema "
    "provisto. Copiás los valores literales del texto sin corregir, calcular ni "
    "redondear. Los montos van SIEMPRE como números JSON con punto decimal, sin "
    "símbolo $, sin separadores de miles y sin texto: 384000.00, nunca "
    "'$200.000,00'. La fecha va YYYY-MM-DD. "
    "Reglas para Factura A con IVA discriminado (columnas 'Subtotal Neto', "
    "'IVA', 'Subtotal c/IVA'): el precio unitario y el subtotal de cada ítem son "
    "SIEMPRE los valores netos SIN IVA (usar 'Subtotal Neto', nunca "
    "'Subtotal c/IVA'). "
    "Reglas para impuestos: es la suma de TODOS los impuestos discriminados al "
    "pie del comprobante (IVA 21% + IVA 10,5% + IVA 27% + percepciones + "
    "impuestos internos + 'Importe Otros Tributos'), no únicamente esa última "
    "fila. Si el pie informa un monto de IVA, impuestos NO es 0. Solo es 0 si el "
    "comprobante no discrimina impuestos (Factura B o C). "
    "Si un campo no aparece en el texto, null; impuestos faltante es 0; salvo "
    "items, fecha_emision, cuit_emisor, razon_social, monto_total y "
    "tipo_comprobante, que son obligatorios."
)

_CARACTERES_MAXIMOS = 30_000  # DESIGN-02 §5: texto truncado a ~30.000 caracteres

_CAMPOS_OBLIGATORIOS = (
    "tipo_comprobante, cuit_emisor, razon_social, fecha_emision, items y monto_total"
)


def build_user_prompt(texto_pdf: str, nombre_archivo: str, intento: int = 1) -> str:
    """Prompt user: nombre de archivo como pista + texto truncado del PDF."""
    texto = texto_pdf[:_CARACTERES_MAXIMOS]
    cuerpo = (
        f"Nombre del archivo: {nombre_archivo}\n\n"
        f"Texto del comprobante:\n{texto}\n\n"
        "Extraé los datos del comprobante en el JSON pedido. Copiá los valores "
        "literales del texto: no corrijas, no calcules ni completes nada."
    )
    if intento > 1:
        cuerpo += (
            f"\n\nATENCIÓN (reintento {intento}): la respuesta anterior no validó contra "
            f"el esquema. Los campos {_CAMPOS_OBLIGATORIOS} son OBLIGATORIOS. Solo "
            "numero_comprobante, numero_orden_compra e impuestos admiten null (impuestos "
            "faltante = 0, p. ej. una Factura B sin impuestos discriminados). Todos los "
            "montos son NÚMEROS con punto decimal, sin '$' ni separadores de miles. "
            "items necesita al menos un elemento con descripcion, cantidad, "
            "precio_unitario y subtotal. En una Factura A con IVA discriminado: "
            "subtotales y precios unitarios netos SIN IVA, e impuestos = suma de todas "
            "las filas de impuestos al pie (IVA 21% + IVA 10,5% + otros tributos); "
            "nunca 0 si hay IVA informado. Si el texto no trae un dato, usá el valor "
            "literal más cercano del documento, nunca lo inventes."
        )
    return cuerpo
