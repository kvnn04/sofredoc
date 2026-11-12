"""Tests de integración de `POST /api/v1/auditar` (VERIFICATION-03 §1, filas 1–7 y 11).

App FastAPI real + SQLite temporal + extractor mock/stub: la matriz de casos
borde se verifica contra la respuesta HTTP y la fila persistida (RN-3-03).
"""

import re

ID_AUDITORIA = re.compile(r"aud_[0-9a-f]{8}")
CREADO_EN = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z")
ARCHIVO_APROBADA = "factura-aprobada-001.pdf"
ARCHIVO_DESVIO = "factura-desvio-monto.pdf"
ARCHIVO_SIN_OC = "factura-monto-alto-sin-oc.pdf"


def _subir(cliente, nombre: str, contenido: bytes, content_type: str = "application/pdf"):
    return cliente.post(
        "/api/v1/auditar",
        files={"file": (nombre, contenido, content_type)},
    )


def _regla(cuerpo: dict, codigo: str) -> dict:
    return next(r for r in cuerpo["reglas_evaluadas"] if r["codigo"] == codigo)


# ------------------------------------------------------------------ filas 1–3
def test_fila_1_flujo_feliz_aprobado(crear_cliente, leer_ejemplo, fila_sqlite):
    """CU-01: 200 APROBADO, 5 reglas verdes, id `aud_*` y fila persistida."""
    cliente = crear_cliente()
    respuesta = _subir(cliente, ARCHIVO_APROBADA, leer_ejemplo(ARCHIVO_APROBADA))

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "APROBADO"
    assert cuerpo["nombre_archivo"] == ARCHIVO_APROBADA
    assert ID_AUDITORIA.fullmatch(cuerpo["id"])

    reglas = cuerpo["reglas_evaluadas"]
    assert [r["codigo"] for r in reglas] == ["R1", "R2", "R3", "R4", "R5"]
    assert all(r["aprobado"] for r in reglas)
    assert _regla(cuerpo, "R1")["mensaje"] == "CUIT válido (dígito verificador correcto)."
    assert _regla(cuerpo, "R4")["mensaje"] == "OC presente."

    datos = cuerpo["datos_extraidos"]
    assert datos["cuit_emisor"] == "30-12345678-1"
    assert datos["fecha_emision"] == "2026-11-07"
    assert datos["monto_total"] == 28200.0  # numérico con 2 decimales (convención)
    assert cuerpo["json_crudo_ia"]["tipo_comprobante"] == "FACTURA"

    # Latencia desglosada por etapa (RN-3-08) y timestamp UTC (convención global).
    assert cuerpo["latencia_extraccion_ms"] >= 0
    assert cuerpo["latencia_reglas_ms"] >= 0
    assert cuerpo["tiempo_ejecucion_ms"] >= max(
        cuerpo["latencia_extraccion_ms"], cuerpo["latencia_reglas_ms"]
    )
    assert CREADO_EN.fullmatch(cuerpo["creado_en"])

    # RN-3-03: persistida antes de responder.
    fila = fila_sqlite(
        "SELECT estado_auditoria, cuit_emisor, monto_total FROM comprobante_auditoria WHERE id = ?",
        (cuerpo["id"],),
    )
    assert fila == ("APROBADO", "30-12345678-1", 28200.0)


def CREATED_EN_OK(cuerpo: dict) -> bool:
    return True


def test_fila_2_desvio_contable(crear_cliente, leer_ejemplo, fila_sqlite):
    """CU-02 (R3): 200 RECHAZADO con DISCREPANCIA_CONTABLE y montos en el mensaje."""
    cliente = crear_cliente(variante="rechazado")
    respuesta = _subir(cliente, ARCHIVO_DESVIO, leer_ejemplo(ARCHIVO_DESVIO))

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "RECHAZADO"

    r3 = _regla(cuerpo, "R3")
    assert r3["aprobado"] is False
    assert r3["codigo_error"] == "DISCREPANCIA_CONTABLE"
    assert "$28.200,00" in r3["mensaje"] and "$30.000,00" in r3["mensaje"]
    assert r3["detalles"] == {"calculado": "28200.00", "declarado": "30000.00"}
    assert all(r["aprobado"] for r in cuerpo["reglas_evaluadas"] if r["codigo"] != "R3")

    fila = fila_sqlite(
        "SELECT estado_auditoria FROM comprobante_auditoria WHERE id = ?", (cuerpo["id"],)
    )
    assert fila == ("RECHAZADO",)


def test_fila_3_tope_sin_orden_compra(crear_cliente, extractor_sin_oc, leer_ejemplo):
    """CU-02 (R4): 200 RECHAZADO con FALTA_ORDEN_COMPRA; R3 sigue en verde."""
    cliente = crear_cliente(extractor=extractor_sin_oc)
    respuesta = _subir(cliente, ARCHIVO_SIN_OC, leer_ejemplo(ARCHIVO_SIN_OC))

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "RECHAZADO"
    assert cuerpo["cuit_emisor"] == "20-12345678-6"
    assert cuerpo["monto_total"] == 650000.0

    r4 = _regla(cuerpo, "R4")
    assert r4["aprobado"] is False
    assert r4["codigo_error"] == "FALTA_ORDEN_COMPRA"
    assert "$650.000,00" in r4["mensaje"] and "$500.000,00" in r4["mensaje"]
    assert _regla(cuerpo, "R3")["aprobado"] is True
    assert all(r["aprobado"] for r in cuerpo["reglas_evaluadas"] if r["codigo"] != "R4")


# ------------------------------------------------------------------ filas 4–7
def test_fila_4_archivo_muy_grande(crear_cliente, fila_sqlite):
    """CU-03: blob de 6 MB → `413 ARCHIVO_MUY_GRANDE` y sin fila persistida."""
    cliente = crear_cliente()
    blob = b"%PDF-1.4" + b"0" * (6 * 1024 * 1024)

    respuesta = _subir(cliente, "grande.pdf", blob)

    assert respuesta.status_code == 413
    error = respuesta.json()["error"]
    assert error["codigo"] == "ARCHIVO_MUY_GRANDE"
    assert "5 MB" in error["mensaje"]
    total = fila_sqlite("SELECT COUNT(*) FROM comprobante_auditoria")
    assert total == (0,)


def test_fila_5_archivo_no_pdf(crear_cliente):
    """CU-03: `.txt` renombrado no pasa la validación de admisión (RN-3-01)."""
    cliente = crear_cliente()

    respuesta = _subir(cliente, "archivo.txt", b"solo texto", content_type="text/plain")

    assert respuesta.status_code == 422
    error = respuesta.json()["error"]
    assert error["codigo"] == "PDF_INVALIDO"
    assert "PDF" in error["mensaje"]


def test_fila_6_pdf_sin_texto(crear_cliente, pdf_en_memoria):
    """Fila 6: PDF escaneado sin capa de texto → `422 PDF_SIN_TEXTO`."""
    cliente = crear_cliente()

    respuesta = _subir(cliente, "escaneado.pdf", pdf_en_memoria([""]))

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "PDF_SIN_TEXTO"


def test_fila_7_extraccion_fallida(crear_cliente, extractor_falla, leer_ejemplo, fila_sqlite):
    """Fila 7: extractor que falla → `502 EXTRACCION_FALLIDA` + fila ERROR_EXTRACCION."""
    cliente = crear_cliente(extractor=extractor_falla)

    respuesta = _subir(cliente, ARCHIVO_APROBADA, leer_ejemplo(ARCHIVO_APROBADA))

    assert respuesta.status_code == 502
    error = respuesta.json()["error"]
    assert error["codigo"] == "EXTRACCION_FALLIDA"

    # RN-3-03: el fallo de extracción queda registrado solo en la tabla.
    fila = fila_sqlite(
        "SELECT estado_auditoria, cuit_emisor, monto_total, datos_extraidos, "
        "reglas_evaluadas, json_crudo_ia FROM comprobante_auditoria"
    )
    assert fila[0] == "ERROR_EXTRACCION"
    assert fila[1] is None and fila[2] is None and fila[3] is None and fila[5] is None
    assert fila[4] == "[]"


# ------------------------------------------------------------------ fila 11 +
def test_fila_11_demasiadas_paginas(crear_cliente, pdf_en_memoria):
    """Fila 11: PDF de 11 páginas → `422 PDF_INVALIDO` con el límite en el mensaje."""
    cliente = crear_cliente()

    respuesta = _subir(cliente, "largo.pdf", pdf_en_memoria([f"Pagina {n}" for n in range(11)]))

    assert respuesta.status_code == 422
    error = respuesta.json()["error"]
    assert error["codigo"] == "PDF_INVALIDO"
    assert "11" in error["mensaje"] and "límite es 10" in error["mensaje"]


def test_extension_pdf_con_mime_desconocido_se_admite(crear_cliente):
    """RN-3-01: extensión `.pdf` basta; el parseo falla luego con `422` tipado."""
    cliente = crear_cliente()

    respuesta = _subir(
        cliente, "sospechoso.pdf", b"no es un pdf", content_type="application/octet-stream"
    )

    assert respuesta.status_code == 422
    assert respuesta.json()["error"]["codigo"] == "PDF_INVALIDO"


def test_remito_no_auditable(crear_cliente, extractor_remito, leer_ejemplo):
    """Solo facturas auditable: REMITO → RECHAZADO por R0 sin evaluar R1–R5."""
    cliente = crear_cliente(extractor=extractor_remito)

    respuesta = _subir(cliente, ARCHIVO_APROBADA, leer_ejemplo(ARCHIVO_APROBADA))

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "RECHAZADO"
    reglas = cuerpo["reglas_evaluadas"]
    assert len(reglas) == 1
    assert reglas[0]["codigo"] == "R0"
    assert reglas[0]["codigo_error"] == "REMITO_NO_AUDITABLE"


def test_ids_de_auditoria_unicos(crear_cliente, leer_ejemplo):
    """RN-3-03: cada auditoría genera un id propio."""
    cliente = crear_cliente()
    contenido = leer_ejemplo(ARCHIVO_APROBADA)

    ids = {_subir(cliente, ARCHIVO_APROBADA, contenido).json()["id"] for _ in range(2)}

    assert len(ids) == 2
