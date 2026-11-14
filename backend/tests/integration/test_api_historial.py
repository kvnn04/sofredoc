"""Tests de integración del historial y ejemplos (VERIFICATION-03 §1, filas 8–10)."""

from decimal import Decimal

from src.domain.models import RegistroAuditoria, ReglaResultado

IDS_ESPERADOS = ["ej-factura-aprobada", "ej-factura-desvio", "ej-monto-alto-sin-oc"]


def _sembrar(repo, ids_con_creado: list[tuple[str, str]]) -> None:
    """Inserta filas con `creado_en` controlado (el orden real depende de SQLite)."""
    for indice, (creado, estado) in enumerate(ids_con_creado):
        repo.guardar(
            RegistroAuditoria(
                id=f"aud_{indice:08x}",
                nombre_archivo=f"factura-{indice}.pdf",
                estado=estado,
                tiempo_ejecucion_ms=100 + indice,
                latencia_extraccion_ms=90 + indice,
                latencia_reglas_ms=1,
                creado_en=creado,
            )
        )


# ------------------------------------------------------------------ fila 8
def test_fila_8_listado_paginado_orden_descendente(crear_cliente):
    """CU-04: limit=2/offset=0 devuelve los 2 más nuevos, sin `json_crudo_ia`."""
    cliente = crear_cliente()
    _sembrar(
        cliente.app.state.auditorias_repo,
        [
            ("2026-11-12T15:00:00Z", "APROBADO"),
            ("2026-11-12T16:00:00Z", "RECHAZADO"),
            ("2026-11-12T17:00:00Z", "APROBADO"),
        ],
    )

    respuesta = cliente.get("/api/v1/historial", params={"limit": 2, "offset": 0})

    assert respuesta.status_code == 200
    items = respuesta.json()
    assert [item["creado_en"] for item in items] == [
        "2026-11-12T17:00:00Z",
        "2026-11-12T16:00:00Z",
    ]
    assert all("json_crudo_ia" not in item for item in items)
    assert items[0]["tiempo_ejecucion_ms"] == 102
    assert items[0]["latencia_extraccion_ms"] == 92
    assert items[0]["latencia_reglas_ms"] == 1


def test_fila_8_offset(crear_cliente):
    """CU-04: offset salta los más nuevos (paginación estable)."""
    cliente = crear_cliente()
    _sembrar(
        cliente.app.state.auditorias_repo,
        [
            ("2026-11-12T15:00:00Z", "APROBADO"),
            ("2026-11-12T16:00:00Z", "RECHAZADO"),
            ("2026-11-12T17:00:00Z", "APROBADO"),
        ],
    )

    respuesta = cliente.get("/api/v1/historial", params={"limit": 2, "offset": 1})

    assert respuesta.status_code == 200
    assert [item["creado_en"] for item in respuesta.json()] == [
        "2026-11-12T16:00:00Z",
        "2026-11-12T15:00:00Z",
    ]


def test_fila_8_limit_por_defecto_y_historial_vacio(crear_cliente):
    """CU-04: sin params usa limit=20/offset=0; con BD vacía responde `[]`."""
    cliente = crear_cliente()

    vacia = cliente.get("/api/v1/historial")
    assert vacia.status_code == 200
    assert vacia.json() == []

    _sembrar(
        cliente.app.state.auditorias_repo,
        [
            ("2026-11-12T15:00:00Z", "APROBADO"),
            ("2026-11-12T16:00:00Z", "APROBADO"),
        ],
    )
    respuesta = cliente.get("/api/v1/historial")
    assert respuesta.status_code == 200
    assert len(respuesta.json()) == 2


def test_fila_8_mismo_segundo_desempate_por_insercion(crear_cliente):
    """CU-04 (ADR-03-08): `creado_en` con precisión de segundos → con empate,
    el desempate es por orden de inserción (`rowid DESC`): el último insertado
    es el "más nuevo". Bug visto en CI (E2E escenario 4): dos auditorías del
    mismo segundo y un `ORDER BY` sin desempate devolvía otra fila como
    "más reciente"."""
    cliente = crear_cliente()
    _sembrar(
        cliente.app.state.auditorias_repo,
        [
            ("2026-11-12T17:00:00Z", "APROBADO"),
            ("2026-11-12T17:00:00Z", "RECHAZADO"),
            ("2026-11-12T17:00:00Z", "RECHAZADO"),
        ],
    )

    respuesta = cliente.get("/api/v1/historial")

    assert respuesta.status_code == 200
    items = respuesta.json()
    assert [item["id"] for item in items] == ["aud_00000002", "aud_00000001", "aud_00000000"]
    assert [item["creado_en"] for item in items] == [
        "2026-11-12T17:00:00Z",
        "2026-11-12T17:00:00Z",
        "2026-11-12T17:00:00Z",
    ]


# ------------------------------------------------------------------ fila 9
def test_fila_9_detalle_completo(crear_cliente):
    """CU-04: el detalle incluye `json_crudo_ia`, reglas y montos redondeados."""
    cliente = crear_cliente()
    cliente.app.state.auditorias_repo.guardar(
        RegistroAuditoria(
            id="aud_9f2c1a7b",
            nombre_archivo="factura-desvio-monto.pdf",
            estado="RECHAZADO",
            cuit_emisor="30-71234567-1",
            monto_total=Decimal("384000.00"),
            datos_extraidos={"cuit_emisor": "30-71234567-1", "monto_total": 384000.0},
            reglas_evaluadas=[
                ReglaResultado(
                    codigo="R3",
                    nombre="Consistencia matemática",
                    aprobado=False,
                    mensaje=(
                        "La suma de ítems + impuestos ($270.000,00) no coincide con el total "
                        "declarado ($285.000,00)."
                    ),
                    codigo_error="DISCREPANCIA_CONTABLE",
                    detalles={"calculado": "270000.00", "declarado": "285000.00"},
                )
            ],
            json_crudo_ia={"tipo_comprobante": "FACTURA", "impuestos": None},
            tiempo_ejecucion_ms=1420,
            latencia_extraccion_ms=1287,
            latencia_reglas_ms=3,
            creado_en="2026-11-12T18:04:05Z",
        )
    )

    respuesta = cliente.get("/api/v1/historial/aud_9f2c1a7b")

    assert respuesta.status_code == 200
    cuerpo = respuesta.json()
    assert cuerpo["estado"] == "RECHAZADO"
    assert cuerpo["monto_total"] == 384000.0
    assert cuerpo["cuit_emisor"] == "30-71234567-1"
    assert cuerpo["json_crudo_ia"] == {"tipo_comprobante": "FACTURA", "impuestos": None}
    assert cuerpo["datos_extraidos"]["monto_total"] == 384000.0
    r3 = cuerpo["reglas_evaluadas"][0]
    assert r3["codigo_error"] == "DISCREPANCIA_CONTABLE"
    assert r3["detalles"] == {"calculado": "270000.00", "declarado": "285000.00"}


def test_fila_9_detalle_404(crear_cliente):
    """CU-04: id inexistente → `404 AUDITORIA_NO_ENCONTRADA` (cuerpo tipado)."""
    cliente = crear_cliente()

    respuesta = cliente.get("/api/v1/historial/aud_inexistente")

    assert respuesta.status_code == 404
    error = respuesta.json()["error"]
    assert error["codigo"] == "AUDITORIA_NO_ENCONTRADA"
    assert "aud_inexistente" in error["mensaje"]


# ------------------------------------------------------------------ fila 10
def test_fila_10_catalogo_de_ejemplos(crear_cliente):
    """CU-05: 3 ejemplos con id, resultado esperado y URL del PDF."""
    cliente = crear_cliente()

    respuesta = cliente.get("/api/v1/ejemplos")

    assert respuesta.status_code == 200
    ejemplos = respuesta.json()
    assert [ejemplo["id"] for ejemplo in ejemplos] == IDS_ESPERADOS
    for ejemplo in ejemplos:
        assert ejemplo["nombre"] and ejemplo["descripcion"]
        assert ejemplo["url_pdf"] == f"/api/v1/ejemplos/{ejemplo['id']}/pdf"
    resultados = {ejemplo["id"]: ejemplo["resultado_esperado"] for ejemplo in ejemplos}
    assert resultados["ej-factura-aprobada"] == "APROBADO"
    assert "R3" in resultados["ej-factura-desvio"]
    assert "R4" in resultados["ej-monto-alto-sin-oc"]


def test_fila_10_pdf_de_ejemplo(crear_cliente):
    """CU-05: el PDF crudo se sirve con `application/pdf` y contenido válido."""
    cliente = crear_cliente()
    for id_ejemplo in IDS_ESPERADOS:
        respuesta = cliente.get(f"/api/v1/ejemplos/{id_ejemplo}/pdf")
        assert respuesta.status_code == 200
        assert respuesta.headers["content-type"].startswith("application/pdf")
        assert respuesta.content.startswith(b"%PDF")
        assert len(respuesta.content) > 0


def test_fila_10_pdf_ejemplo_404(crear_cliente):
    """CU-05: id desconocido → `404 EJEMPLO_NO_ENCONTRADO`."""
    cliente = crear_cliente()

    respuesta = cliente.get("/api/v1/ejemplos/no-existe/pdf")

    assert respuesta.status_code == 404
    assert respuesta.json()["error"]["codigo"] == "EJEMPLO_NO_ENCONTRADO"


def test_fila_10_pdf_ejemplo_no_generado(crear_cliente, tmp_path):
    """CU-05: PDF faltante (script no ejecutado) → `404` con hint del script."""
    cliente = crear_cliente()
    cliente.app.state.directorio_ejemplos = tmp_path / "vacío"

    respuesta = cliente.get("/api/v1/ejemplos/ej-factura-aprobada/pdf")

    assert respuesta.status_code == 404
    error = respuesta.json()["error"]
    assert error["codigo"] == "EJEMPLO_NO_ENCONTRADO"
    assert "generar_ejemplos" in error["mensaje"]
