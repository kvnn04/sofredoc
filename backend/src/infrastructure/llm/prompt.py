"""Prompts de extracción con Structured Outputs (DESIGN-02 §5).

La IA solo extrae (RN-2-06): copia valores literales del texto sin corregir,
calcular ni redondear. La validación final es de Pydantic, no del prompt.
"""

SYSTEM_PROMPT = (
    "Sos un extractor de datos de comprobantes comerciales argentinos. "
    "Devolvés EXCLUSIVAMENTE un JSON conforme al esquema provisto. "
    "Copiás los valores literales del texto sin corregir, calcular ni redondear. "
    "Los montos van como números con punto decimal. La fecha va YYYY-MM-DD. "
    "Si un campo no aparece en el texto, null, salvo items, fecha_emision, "
    "cuit_emisor, razon_social, monto_total y tipo_comprobante, que son obligatorios."
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
            "numero_comprobante, numero_orden_compra e impuestos admiten null. items "
            "necesita al menos un elemento con descripcion, cantidad, precio_unitario "
            "y subtotal. Si el texto no trae un dato, usá el valor literal más cercano "
            "del documento, nunca lo inventes."
        )
    return cuerpo
