"""Tests unitarios de MOD-02: pypdf, mock y LLM falsificado (VERIFICATION-02 §1).

Sin I/O real: el SDK `openai` se reemplaza por un módulo falso y las respuestas
del LLM por dicts. Los PDFs se generan en memoria sin dependencias extra.
"""

import json
import sys
import time
import types
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest

import src.infrastructure.llm.client as cliente_llm
import src.infrastructure.llm.structured_extractor as modulo_extractor
import src.infrastructure.pdf.pypdf_adapter as pypdf_adapter
from src.config import get_settings
from src.domain.errors import (
    ExtraccionFallidaError,
    PdfDemasiadasPaginasError,
    PdfInvalidoError,
    PdfSinTextoError,
)
from src.domain.models import FacturaExtraida
from src.domain.ports.document_extractor_port import DocumentExtractorPort
from src.domain.ports.pdf_text_port import PdfTextPort
from src.infrastructure.llm.factory import crear_extractor
from src.infrastructure.llm.mock_extractor import MockExtractor
from src.infrastructure.llm.structured_extractor import LLMStructuredExtractor
from src.infrastructure.pdf.pypdf_adapter import PypdfTextExtractor

RUTA_FIXTURES = Path(__file__).resolve().parents[2] / "data" / "fixtures"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _pdf(textos: list[str]) -> bytes:
    """Arma un PDF de N páginas con un stream de texto por página (sin fpdf2)."""
    total = len(textos)
    kids = " ".join(f"{4 + 2 * i} 0 R" for i in range(total))
    objetos: list[bytes] = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        f"<< /Type /Pages /Kids [{kids}] /Count {total} >>".encode(),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    for i, texto in enumerate(textos):
        objetos.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            f"/Resources << /Font << /F1 3 0 R >> >> /Contents {5 + 2 * i} 0 R >>".encode()
        )
        stream = f"BT /F1 12 Tf 72 720 Td ({texto}) Tj ET".encode()
        objetos.append(f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream")

    salida = bytearray(b"%PDF-1.4\n")
    offsets: list[int] = []
    for numero, cuerpo in enumerate(objetos, start=1):
        offsets.append(len(salida))
        salida += f"{numero} 0 obj\n".encode() + cuerpo + b"\nendobj\n"
    xref = len(salida)
    salida += f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n".encode()
    for desplazamiento in offsets:
        salida += f"{desplazamiento:010d} 00000 n \n".encode()
    salida += (
        f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF".encode()
    )
    return bytes(salida)


class ClienteFalso:
    """`completar_con_esquema` falsificado: consume la lista de respuestas en orden."""

    def __init__(self, respuestas: list[Any]) -> None:
        self.respuestas = list(respuestas)
        self.llamadas: list[dict[str, Any]] = []

    def __call__(self, **kwargs: Any) -> dict[str, Any]:
        self.llamadas.append(kwargs)
        respuesta = self.respuestas.pop(0)
        if isinstance(respuesta, Exception):
            raise respuesta
        return respuesta


def _parchear_config(monkeypatch: pytest.MonkeyPatch, api_key: str | None = "sk-test") -> None:
    """Reemplaza `get_settings` dentro de client.py con una config de prueba."""
    config = types.SimpleNamespace(llm_api_key=api_key, llm_model="gpt-test", llm_provider="openai")
    monkeypatch.setattr(cliente_llm, "get_settings", lambda: config)


def _parchear_sdk(
    monkeypatch: pytest.MonkeyPatch,
    contenido: str | None = None,
    error: Exception | None = None,
) -> list[dict[str, Any]]:
    """Reemplaza el módulo `openai` por uno falso; devuelve las llamadas grabadas."""
    llamadas: list[dict[str, Any]] = []

    class FalsasCompletions:
        def create(self, **kwargs: Any) -> Any:
            llamadas.append(kwargs)
            if error is not None:
                raise error
            mensaje = types.SimpleNamespace(content=contenido)
            return types.SimpleNamespace(choices=[types.SimpleNamespace(message=mensaje)])

    class FalsoOpenAI:
        def __init__(self, api_key: str | None = None) -> None:
            self.api_key = api_key
            self.chat = types.SimpleNamespace(completions=FalsasCompletions())

    falso = types.ModuleType("openai")
    falso.OpenAI = FalsoOpenAI  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, "openai", falso)
    return llamadas


@pytest.fixture
def factura_cruda(factura):  # noqa: ANN201 — fixture factory del conftest
    """Dict serializado de una `FacturaExtraida` válida (como lo devolvería el LLM)."""

    def _factory(**overrides) -> dict[str, Any]:
        return json.loads(factura(**overrides).model_dump_json())

    return _factory


# ---------------------------------------------------------------------------
# Contratos de puertos (MOD-03 los cablea; aquí se verifica que existen)
# ---------------------------------------------------------------------------
class TestPuertos:
    def test_puertos_exponen_los_contratos_de_mod02(self):
        assert hasattr(PdfTextPort, "extraer_texto")
        assert hasattr(DocumentExtractorPort, "extraer")


# ---------------------------------------------------------------------------
# T-10: PypdfTextExtractor
# ---------------------------------------------------------------------------
class TestPypdfTextExtractor:
    def test_pdf_con_texto_devuelve_concatenado(self):
        pdf = _pdf(["CUIT: 30-12345678-1", "Fecha: 2026-11-07 Total: 28200.00"])

        texto = PypdfTextExtractor().extraer_texto(pdf)

        assert "30-12345678-1" in texto
        assert "28200.00" in texto
        assert "\n" in texto  # concatena las páginas

    def test_pdf_de_10_paginas_en_el_limite(self):
        pdf = _pdf([f"pagina {i:02d} contenido suficiente" for i in range(10)])

        texto = PypdfTextExtractor().extraer_texto(pdf)

        assert "pagina 09" in texto

    def test_pdf_de_11_paginas_supera_el_limite(self):
        pdf = _pdf([f"pagina {i:02d}" for i in range(11)])

        with pytest.raises(PdfDemasiadasPaginasError, match="11 páginas"):
            PypdfTextExtractor().extraer_texto(pdf)

    def test_pdf_corrupto_lanza_invalido(self):
        with pytest.raises(PdfInvalidoError):
            PypdfTextExtractor().extraer_texto(b"esto no es un pdf")

    def test_pdf_cifrado_lanza_invalido(self, monkeypatch):
        monkeypatch.setattr(
            pypdf_adapter, "PdfReader", lambda *_a, **_k: types.SimpleNamespace(is_encrypted=True)
        )

        with pytest.raises(PdfInvalidoError, match="cifrado"):
            PypdfTextExtractor().extraer_texto(b"%PDF-falso")

    def test_paginas_ilegibles_lanzan_invalido(self, monkeypatch):
        class LectorRoto:
            is_encrypted = False

            @property
            def pages(self):
                raise ValueError("árbol de páginas corrupto")

        monkeypatch.setattr(pypdf_adapter, "PdfReader", lambda *_a, **_k: LectorRoto())

        with pytest.raises(PdfInvalidoError, match="ilegible"):
            PypdfTextExtractor().extraer_texto(b"%PDF-falso")

    def test_extract_text_roto_lanza_invalido(self, monkeypatch):
        class PaginaRota:
            def extract_text(self) -> str:
                raise ValueError("content stream corrupto")

        lector = types.SimpleNamespace(is_encrypted=False, pages=[PaginaRota()])
        monkeypatch.setattr(pypdf_adapter, "PdfReader", lambda *_a, **_k: lector)

        with pytest.raises(PdfInvalidoError, match="extraer el texto"):
            PypdfTextExtractor().extraer_texto(b"%PDF-falso")

    def test_pdf_sin_texto_lanza_sin_texto(self):
        pdf = _pdf([""])  # página sin texto embebido (escaneo simulado)

        with pytest.raises(PdfSinTextoError):
            PypdfTextExtractor().extraer_texto(pdf)

    def test_texto_corto_cuenta_como_sin_texto(self):
        pdf = _pdf(["a b c"])  # 3 caracteres significativos < 20

        with pytest.raises(PdfSinTextoError):
            PypdfTextExtractor().extraer_texto(pdf)


# ---------------------------------------------------------------------------
# T-11: MockExtractor
# ---------------------------------------------------------------------------
class TestMockExtractor:
    def test_determinista_misma_entrada_misma_salida(self):
        extractor = MockExtractor(RUTA_FIXTURES, "aprobada")

        primera = extractor.extraer("texto", "f.pdf")
        segunda = extractor.extraer("texto", "f.pdf")

        assert primera.model_dump() == segunda.model_dump()
        assert primera.factura.cuit_emisor == "30-12345678-1"
        assert primera.json_crudo_ia is not None

    def test_variantes_validas_contra_el_esquema(self):
        for variante in ("aprobada", "rechazado", "monto-alto-sin-oc", "remito"):
            resultado = MockExtractor(RUTA_FIXTURES, variante).extraer("x", "y")
            FacturaExtraida.model_validate(resultado.json_crudo_ia)  # no lanza

    def test_aprobada_es_matematicamente_consistente(self):
        factura = MockExtractor(RUTA_FIXTURES, "aprobada").extraer("x", "y").factura
        suma = sum((item.subtotal for item in factura.items), Decimal("0.00"))

        assert factura.monto_total == suma + factura.impuestos

    def test_rechazado_desvia_mas_de_un_peso_para_r3(self):
        factura = MockExtractor(RUTA_FIXTURES, "rechazado").extraer("x", "y").factura
        suma = sum((item.subtotal for item in factura.items), Decimal("0.00"))
        desvio = abs(factura.monto_total - (suma + factura.impuestos))

        assert desvio > Decimal("1.00")

    def test_ejemplos_de_la_demo_resuelven_su_fixture(self):
        """Matriz de verdad de MOD-03 reproducible en modo mock (ADR-05-01)."""
        extractor = MockExtractor(RUTA_FIXTURES, "aprobada")

        aprobada = extractor.extraer("x", "ej-factura-aprobada.pdf").factura
        desvio = extractor.extraer("x", "ej-factura-desvio.pdf").factura
        monto_alto = extractor.extraer("x", "ej-monto-alto-sin-oc.pdf").factura

        assert aprobada.numero_orden_compra == "OC-2026-0042"  # sin R3 ni R4
        suma = sum((item.subtotal for item in desvio.items), Decimal("0.00"))
        assert abs(desvio.monto_total - (suma + desvio.impuestos)) > Decimal("1.00")  # R3
        assert monto_alto.monto_total > Decimal("500000")  # dispara R4 (tope estricto)
        assert monto_alto.numero_orden_compra is None

    def test_remito_dispara_la_fixture_remito(self):
        """Archivo con 'remito' en el nombre → fixture REMITO (el motor ya cubre R0)."""
        extractor = MockExtractor(RUTA_FIXTURES, "aprobada")  # la variante da igual

        factura = extractor.extraer("x", "remito-transporte-2026.pdf").factura

        assert factura.tipo_comprobante == "REMITO"

    def test_archivo_original_del_ejemplo_resubido_tambien_resuelve(self):
        """Si el usuario descarga el PDF y lo re-sube, conserva su escenario."""
        extractor = MockExtractor(RUTA_FIXTURES, "aprobada")

        factura = extractor.extraer("x", "factura-monto-alto-sin-oc.pdf").factura

        assert factura.monto_total > Decimal("500000")
        assert factura.numero_orden_compra is None

    def test_nombre_desconocido_cae_en_la_variante_configurada(self):
        esperado = MockExtractor(RUTA_FIXTURES, "rechazado").extraer("x", "y")

        resultado = MockExtractor(RUTA_FIXTURES, "rechazado").extraer("x", "comprobante.pdf")

        assert resultado.model_dump() == esperado.model_dump()

    def test_variante_invalida_falla_rapido(self):
        with pytest.raises(ValueError, match="MOCK_VARIANT"):
            MockExtractor(RUTA_FIXTURES, "no-existe")

    def test_fixture_ausente_lanza_extraccion_fallida(self, tmp_path):
        with pytest.raises(ExtraccionFallidaError, match="Fixture mock"):
            MockExtractor(tmp_path, "aprobada")

    def test_respuesta_en_menos_de_10_ms(self):
        extractor = MockExtractor(RUTA_FIXTURES, "aprobada")

        inicio = time.perf_counter()
        extractor.extraer("texto", "f.pdf")
        transcurrido = time.perf_counter() - inicio

        assert transcurrido < 0.010  # CU-04: < 10 ms


# ---------------------------------------------------------------------------
# T-12: LLMStructuredExtractor con cliente falsificado
# ---------------------------------------------------------------------------
class TestLLMStructuredExtractor:
    def test_respuesta_valida_conserva_json_crudo(self, monkeypatch, factura_cruda):
        crudo = factura_cruda()
        falso = ClienteFalso([crudo])
        monkeypatch.setattr(modulo_extractor, "completar_con_esquema", falso)

        resultado = LLMStructuredExtractor("openai", "gpt-test").extraer("texto", "f.pdf")

        assert resultado.factura.monto_total == Decimal("25000.00")
        assert resultado.json_crudo_ia == crudo  # RN-2-04
        assert len(falso.llamadas) == 1
        assert "reintento" not in falso.llamadas[0]["user"]
        assert falso.llamadas[0]["temperatura"] == 0

    def test_reintenta_una_vez_y_puede_salir_bien(self, monkeypatch, factura_cruda):
        invalido = {"tipo_comprobante": "FACTURA"}  # sin campos obligatorios
        falso = ClienteFalso([invalido, factura_cruda()])
        monkeypatch.setattr(modulo_extractor, "completar_con_esquema", falso)

        resultado = LLMStructuredExtractor("openai", "gpt-test").extraer("texto", "f.pdf")

        assert len(falso.llamadas) == 2  # intento inicial + 1 reintento (RN-2-03)
        assert "OBLIGATORIOS" in falso.llamadas[1]["user"]  # prompt reforzado
        assert resultado.factura.razon_social == "Distribuidora Andina S.A."

    def test_falla_definitivamente_tras_reintento(self, monkeypatch):
        invalido = {"tipo_comprobante": "FACTURA"}
        falso = ClienteFalso([invalido, invalido])
        monkeypatch.setattr(modulo_extractor, "completar_con_esquema", falso)

        with pytest.raises(ExtraccionFallidaError) as excinfo:
            LLMStructuredExtractor("openai", "gpt-test").extraer("texto", "f.pdf")

        assert excinfo.value.codigo == "EXTRACCION_FALLIDA"
        assert "2 intentos" in excinfo.value.mensaje
        assert len(falso.llamadas) == 2  # no reintenta más allá del límite

    def test_error_del_proveedor_no_consume_reintento(self, monkeypatch):
        # El fallo del proveedor llega tipificado desde client.py (ver TestClienteLLM)
        # y el extractor no lo reintenta: el reintento es solo sobre ValidationError.
        falso = ClienteFalso([ExtraccionFallidaError("Error del proveedor LLM: timeout")])
        monkeypatch.setattr(modulo_extractor, "completar_con_esquema", falso)

        with pytest.raises(ExtraccionFallidaError, match="timeout"):
            LLMStructuredExtractor("openai", "gpt-test").extraer("texto", "f.pdf")

        assert len(falso.llamadas) == 1


# ---------------------------------------------------------------------------
# T-12 (complemento): client.py con SDK openai falsificado
# ---------------------------------------------------------------------------
class TestClienteLLM:
    def test_llama_con_temperature_0_y_esquema_estricto(self, monkeypatch, factura_cruda):
        _parchear_config(monkeypatch)
        contenido = json.dumps(factura_cruda())
        llamadas = _parchear_sdk(monkeypatch, contenido=contenido)
        esquema = FacturaExtraida.model_json_schema()

        crudo = cliente_llm.completar_con_esquema(
            system="S", user="U", esquema_json=esquema, temperatura=0
        )

        assert crudo["razon_social"] == factura_cruda()["razon_social"]
        assert llamadas[0]["temperature"] == 0
        assert llamadas[0]["model"] == "gpt-test"
        formato = llamadas[0]["response_format"]
        assert formato["type"] == "json_schema"
        assert formato["json_schema"]["strict"] is True
        assert formato["json_schema"]["schema"]["additionalProperties"] is False

    def test_sin_api_key_lanza_extraccion_fallida(self, monkeypatch):
        _parchear_config(monkeypatch, api_key=None)

        with pytest.raises(ExtraccionFallidaError, match="LLM_API_KEY"):
            cliente_llm.completar_con_esquema("S", "U", {}, temperatura=0)

    def test_sdk_ausente_lanza_extraccion_fallida(self, monkeypatch):
        _parchear_config(monkeypatch)
        monkeypatch.setitem(sys.modules, "openai", None)  # `from openai import ...` => ImportError

        with pytest.raises(ExtraccionFallidaError, match="openai"):
            cliente_llm.completar_con_esquema("S", "U", {}, temperatura=0)

    def test_error_del_proveedor_lanza_extraccion_fallida(self, monkeypatch):
        _parchear_config(monkeypatch)
        _parchear_sdk(monkeypatch, error=RuntimeError("cupo agotado"))

        with pytest.raises(ExtraccionFallidaError, match="proveedor"):
            cliente_llm.completar_con_esquema("S", "U", {}, temperatura=0)

    def test_respuesta_no_json_lanza_extraccion_fallida(self, monkeypatch):
        _parchear_config(monkeypatch)
        _parchear_sdk(monkeypatch, contenido="lo siento, no es json")

        with pytest.raises(ExtraccionFallidaError, match="JSON válido"):
            cliente_llm.completar_con_esquema("S", "U", {}, temperatura=0)


class TestEsquemaEstricto:
    def _visitar(self, nodo: Any):
        if isinstance(nodo, list):
            for item in nodo:
                yield from self._visitar(item)
        elif isinstance(nodo, dict):
            yield nodo
            for valor in nodo.values():
                yield from self._visitar(valor)

    def test_sin_claves_no_soportadas_por_strict(self):
        esquema = cliente_llm.preparar_esquema_estricto(FacturaExtraida.model_json_schema())
        texto = json.dumps(esquema)

        for prohibida in (
            "title",
            "default",
            "minLength",
            "minItems",
            "minimum",
            "exclusiveMinimum",
        ):
            assert f'"{prohibida}"' not in texto

    def test_todos_los_objetos_requeridos_y_cerrados(self):
        esquema = cliente_llm.preparar_esquema_estricto(FacturaExtraida.model_json_schema())
        objetos = [n for n in self._visitar(esquema) if "properties" in n]

        assert len(objetos) >= 2  # FacturaExtraida + ItemFactura ($defs)
        for objeto in objetos:
            assert objeto["additionalProperties"] is False
            assert set(objeto["required"]) == set(objeto["properties"])

    def test_decimal_se_convierte_en_numero_unico(self):
        # Decimal genera anyOf [{number}, {string}]: en strict el proveedor puede
        # elegir la rama string y devolver '$200.000,00', que Pydantic rechaza.
        esquema = cliente_llm.preparar_esquema_estricto(FacturaExtraida.model_json_schema())

        assert esquema["properties"]["monto_total"] == {"type": "number"}
        assert esquema["properties"]["impuestos"] == {"type": "number"}
        item = esquema["$defs"]["ItemFactura"]["properties"]
        assert item["cantidad"] == {"type": "number"}
        assert item["precio_unitario"] == {"type": "number"}
        assert item["subtotal"] == {"type": "number"}

    def test_anyof_decimal_acepta_orden_inverso(self):
        esquema = {"anyOf": [{"type": "string"}, {"type": "number"}]}

        assert cliente_llm.preparar_esquema_estricto(esquema) == {"type": "number"}

    def test_conserva_enum_format_y_null_de_opcionales(self):
        esquema = cliente_llm.preparar_esquema_estricto(FacturaExtraida.model_json_schema())
        propiedades = esquema["properties"]

        assert propiedades["tipo_comprobante"]["enum"] == ["FACTURA", "REMITO"]
        assert propiedades["fecha_emision"]["format"] == "date"
        assert {"type": "null"} in propiedades["numero_comprobante"]["anyOf"]
        assert esquema["$defs"]["ItemFactura"]["properties"]["descripcion"]["type"] == "string"

    def test_limpia_formas_defensivas_de_otros_generadores(self):
        # `items` como lista (validación por tupla) y valores escalares: formas
        # que pydantic no emite pero que otros generadores de JSON Schema sí.
        esquema = {"items": [{"type": "string"}, 7]}

        limpio = cliente_llm.preparar_esquema_estricto(esquema)

        assert limpio == {"items": [{"type": "string"}, 7]}


# ---------------------------------------------------------------------------
# T-13: factory.py
# ---------------------------------------------------------------------------
class TestFactory:
    def _config(self, mode: str, api_key: str | None = None, variante: str = "aprobada"):
        return types.SimpleNamespace(
            extractor_mode=mode,
            llm_api_key=api_key,
            llm_provider="openai",
            llm_model="gpt-test",
            mock_variant=variante,
        )

    def test_mock_es_el_default_sin_config(self, monkeypatch):
        # Determinista aunque el desarrollador tenga backend/.env con llm:
        # las variables de entorno reales tienen prioridad sobre el archivo.
        monkeypatch.setenv("EXTRACTOR_MODE", "mock")
        get_settings.cache_clear()
        try:
            extractor = crear_extractor()  # default => EXTRACTOR_MODE=mock
        finally:
            get_settings.cache_clear()

        assert isinstance(extractor, MockExtractor)

    def test_llama_mock_con_la_variante_configurada(self):
        config = self._config("mock", variante="rechazado")

        resultado = crear_extractor(config).extraer("x", "f.pdf")

        assert resultado.factura.monto_total == Decimal("30000.00")

    def test_llm_con_api_key(self):
        extractor = crear_extractor(self._config("llm", api_key="sk-test"))

        assert isinstance(extractor, LLMStructuredExtractor)
        assert extractor._proveedor == "openai"  # noqa: SLF001 — test de construcción

    def test_llm_sin_api_key_error_claro(self):
        with pytest.raises(RuntimeError, match="LLM_API_KEY"):
            crear_extractor(self._config("llm", api_key=None))
