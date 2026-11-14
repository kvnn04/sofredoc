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
    "'$200.000,00'. Copiá cada monto dígito a dígito tal como está impreso: no "
    "lo aproximes, no lo redondees y no lo calcules por tu cuenta. La fecha va "
    "YYYY-MM-DD. "
    "ANCLA: primero extraé letra_comprobante del encabezado (la letra sola de "
    "'FACTURA A', 'FACTURA B', etc.); esa letra define cómo leer los montos: "
    "- Factura A (IVA discriminado): el precio unitario y el subtotal de cada "
    "ítem son los valores netos SIN IVA (columna 'Subtotal Neto', nunca "
    "'Subtotal c/IVA'). "
    "- Factura B o C (IVA incluido en el precio): el precio unitario y el "
    "subtotal de cada ítem son el importe final de la línea (IVA incluido). "
    "detalle_impuestos: cargá CADA línea de impuesto o tributo discriminada al "
    "pie, UNA entrada por línea, con el concepto literal y el monto de ESA "
    "línea sola: 'IVA 21%', 'IVA 10,5%', 'IVA 27%', impuestos internos, "
    "percepciones (IIBB ARBA, IVA, SIRTAC) y 'Importe Otros Tributos'. NO "
    "sumes impuestos ni precargues totales: un elemento por línea, montos "
    "separados (la suma la calcula el sistema). Excluí SIEMPRE los desgloses "
    "informativos del Régimen de Transparencia Fiscal al Consumidor (Ley "
    "27.743) — 'IVA Contenido' / 'IVA Contenido (incluido en el precio final)' "
    "y 'Otros Impuestos Nacionales Indirectos' — porque ya están INCLUIDOS en "
    "el total y en los subtotales de los ítems. Si un mismo tributo aparece "
    "dos veces — en una tabla de desglose (p. ej. 'DETALLE DE OTROS TRIBUTOS / "
    "PERCEPCIONES') y además en la línea agregada del pie ('Importe Otros "
    "Tributos') — es EL MISMO monto: cargalo UNA sola vez, nunca lo "
    "dupliques. Si el pie no discrimina líneas, devolvé la lista vacía. "
    "numero_comprobante: combiná literalmente Punto de Venta (5 dígitos) + "
    "'-' + Comp. Nro (8 dígitos) tal como figuran en el comprobante: "
    "'00005-00019384', nunca solo '00019384'. "
    "Si un campo no aparece en el texto, null (las listas, vacías); salvo "
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
            "numero_comprobante y numero_orden_compra admiten null (las listas van "
            "vacías, no null). Todos los montos son NÚMEROS con punto decimal, sin "
            "'$' ni separadores de miles. "
            "items necesita al menos un elemento con descripcion, cantidad, "
            "precio_unitario y subtotal. "
            "VERIFICACIÓN ARITMÉTICA: la suma de (cantidad × precio unitario) de "
            "los ítems más cada monto de detalle_impuestos debe coincidir con el "
            "IMPORTE TOTAL (tolerancia ± $1.00). Re-copiá dígito a dígito los "
            "montos del pie tal como están impresos: no los aproximes ni los "
            "calcules por tu cuenta. "
            "detalle_impuestos: una entrada por CADA línea de impuesto discriminada "
            "al pie (IVA 21%, IVA 10,5%, percepciones IIBB/IVA, otros tributos), con "
            "el concepto literal y el monto de ESA línea sola; NUNCA sumes impuestos "
            "ni cargues totales; excluye el 'IVA Contenido (Ley 27.743)' porque es "
            "informativo y ya está incluido en el total; si un tributo figura en una "
            "tabla de desglose Y en la línea 'Importe Otros Tributos' del pie, es el "
            "mismo monto: cargalo UNA sola vez. En una Factura A con IVA "
            "discriminado: subtotales y precios unitarios netos SIN IVA. En una "
            "Factura B o C: subtotales con IVA incluido. "
            "numero_comprobante: 'PPPPP-NNNNNNNN' (Punto de Venta de 5 dígitos + "
            "guion + Comp. Nro de 8 dígitos, p. ej. '00005-00019384'). Si el texto "
            "no trae un dato, usá el valor literal más cercano del documento, "
            "nunca lo inventes."
        )
    return cuerpo
