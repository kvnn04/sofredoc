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
    "ANCLA: primero extraé letra_comprobante del encabezado (la letra sola de "
    "'FACTURA A', 'FACTURA B', etc.); esa letra define cómo leer los montos: "
    "- Factura A (IVA discriminado): el precio unitario y el subtotal de cada "
    "ítem son los valores netos SIN IVA (columna 'Subtotal Neto', nunca "
    "'Subtotal c/IVA'); impuestos = suma de TODOS los impuestos discriminados "
    "que se suman al pie (IVA 21% + IVA 10,5% + IVA 27% + percepciones + "
    "impuestos internos + 'Importe Otros Tributos'); si el pie informa un monto "
    "de IVA, impuestos NO es 0. "
    "- Factura B o C (IVA incluido en el precio): el precio unitario y el "
    "subtotal de cada ítem son el importe final de la línea (IVA incluido); "
    "impuestos = 0 si entre los subtotales de los ítems y el total no se suma "
    "nada. "
    "En NINGÚN caso cargues en impuestos los desgloses informativos del Régimen "
    "de Transparencia Fiscal al Consumidor (Ley 27.743): 'IVA Contenido' / 'IVA "
    "Contenido (incluido en el precio final)' y 'Otros Impuestos Nacionales "
    "Indirectos' ya están INCLUIDOS en el total y en los subtotales de los "
    "ítems, no se adicionan. Solo van a impuestos las percepciones u otros "
    "tributos que figuren como línea ADICIONAL entre los subtotales y el total "
    "(p. ej. 'Percepciones / Otros Tributos' con un monto mayor a 0). "
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
            "nunca 0 si hay IVA informado. En una Factura B o C: subtotales con "
            "IVA incluido e impuestos = 0; el 'IVA Contenido (Ley 27.743)' del "
            "pie es informativo, ya está incluido en el total y NO se suma a "
            "impuestos. Si el texto no trae un dato, usá el valor "
            "literal más cercano del documento, nunca lo inventes."
        )
    return cuerpo
