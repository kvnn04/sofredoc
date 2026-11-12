"""Cliente del proveedor de Structured Outputs (DESIGN-02 §4).

Único archivo que conoce el SDK: cambiar de proveedor toca solo este módulo.
La clave/modelo se leen de la configuración (`LLM_API_KEY`, `LLM_MODEL`);
el SDK se importa en perezoso para que el modo mock no lo necesite.
"""

import json
import logging
from typing import Any

from src.config import get_settings
from src.domain.errors import ExtraccionFallidaError

logger = logging.getLogger(__name__)

_NOMBRE_ESQUEMA = "FacturaExtraida"

# Claves JSON Schema aceptadas por el modo strict del proveedor; todo lo demás
# (title, default, minLength, minItems, minimum, ...) provoca rechazo de la API.
_CLAVES_ESTRUCTURADAS = frozenset(
    {
        "$defs",
        "$ref",
        "additionalProperties",
        "allOf",
        "anyOf",
        "description",
        "enum",
        "format",
        "items",
        "oneOf",
        "properties",
        "required",
        "type",
    }
)


def preparar_esquema_estricto(esquema: dict[str, Any]) -> dict[str, Any]:
    """Adapta el JSON Schema de Pydantic al modo `strict` del proveedor.

    - Quita claves no soportadas (`title`, `default`, `minLength`, `minItems`,
      `minimum`...): las restricciones reales las aplica Pydantic (RN-2-03).
    - Marca `additionalProperties: false` y `required` con TODAS las propiedades
      (exigencia del proveedor); los opcionales siguen admitiendo `null` vía anyOf.
    """
    return _limpiar(esquema)


def _limpiar(nodo: Any) -> Any:
    if isinstance(nodo, list):
        return [_limpiar(item) for item in nodo]
    if not isinstance(nodo, dict):
        return nodo
    resultado: dict[str, Any] = {}
    for clave, valor in nodo.items():
        if clave not in _CLAVES_ESTRUCTURADAS:
            continue
        if clave in ("properties", "$defs"):
            resultado[clave] = {nombre: _limpiar(hijo) for nombre, hijo in valor.items()}
        elif clave in ("anyOf", "allOf", "oneOf"):
            resultado[clave] = [_limpiar(rama) for rama in valor]
        elif clave in ("items",):
            resultado[clave] = _limpiar(valor)
        else:
            resultado[clave] = valor
    if "properties" in resultado:
        resultado["required"] = list(resultado["properties"])
        resultado["additionalProperties"] = False
    return resultado


def completar_con_esquema(
    system: str,
    user: str,
    esquema_json: dict[str, Any],
    temperatura: float,
) -> dict[str, Any]:
    """Una llamada al proveedor con `response_format` JSON Schema; devuelve el dict crudo.

    Errores del proveedor o respuestas no-JSON se tipifican como
    `ExtraccionFallidaError` (EXTRACCION_FALLIDA, DESIGN-02 §5).
    """
    config = get_settings()
    if not config.llm_api_key:
        raise ExtraccionFallidaError(
            "EXTRACTOR_MODE=llm requiere LLM_API_KEY configurada (backend/.env)."
        )

    try:
        from openai import OpenAI  # import perezoso: el modo mock no requiere SDK
    except ImportError as exc:
        raise ExtraccionFallidaError(
            "El SDK 'openai' no está instalado; ejecutá `pip install -r requirements.txt`."
        ) from exc

    cliente = OpenAI(api_key=config.llm_api_key)
    logger.debug(
        "LLM %s/%s | temperatura=%s | texto=%d chars",
        config.llm_provider,
        config.llm_model,
        temperatura,
        len(user),
    )
    try:
        respuesta = cliente.chat.completions.create(
            model=config.llm_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": _NOMBRE_ESQUEMA,
                    "strict": True,
                    "schema": preparar_esquema_estricto(esquema_json),
                },
            },
            temperature=temperatura,
        )
    except Exception as exc:
        logger.error("Fallo del proveedor LLM: %s", exc)
        raise ExtraccionFallidaError(
            f"Error del proveedor LLM ({config.llm_provider}/{config.llm_model}): {exc}"
        ) from exc

    contenido = respuesta.choices[0].message.content
    try:
        return json.loads(contenido)
    except (TypeError, ValueError) as exc:
        raise ExtraccionFallidaError(
            f"El proveedor no devolvió JSON válido: {str(contenido)[:200]!r}"
        ) from exc
