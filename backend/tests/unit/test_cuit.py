"""Pruebas del Value Object CUIT (módulo 11) — T-14 y matriz de casos borde R1."""

import pytest

from src.domain.value_objects.cuit import CUIT

VALIDOS = [
    "30-12345678-1",  # fila 1: con guiones
    "30123456781",  # fila 2: sin guiones
    "30-71234567-1",
    "20-12345678-6",
    "20-87654321-5",
    "  30-12345678-1  ",  # espacios en los extremos se normalizan
]

INVALIDOS = [
    "30-12345678-9",  # fila 3: DV incorrecto
    "30-12345678",  # fila 4: 10 dígitos
    "30-1234567A-1",  # fila 5: letras
    "",  # fila 5: vacío
    "30 12345678 1",  # espacios internos: 13 caracteres
    "30-12345678-10",  # 12 caracteres
]


@pytest.mark.parametrize("valor", VALIDOS)
def test_cuit_valido(valor: str) -> None:
    cuit = CUIT(valor)
    assert cuit.formato_valido()
    assert cuit.digito_verificador_valido()
    assert cuit.es_valido()


@pytest.mark.parametrize("valor", INVALIDOS)
def test_cuit_invalido(valor: str) -> None:
    assert not CUIT(valor).es_valido()


def test_dv_cae_en_cero_rama_dv11() -> None:
    """Suma ponderada 176, resto 0 → dv = 11 → se mapea a 0 (fila 6)."""
    cuit = CUIT("27-12345678-0")
    assert cuit.digito_verificador_valido()
    assert cuit.es_valido()


def test_dv_cae_en_nueve_rama_dv10() -> None:
    """Suma ponderada 155, resto 1 → dv = 10 → se mapea a 9 (fila 7)."""
    cuit = CUIT("30-12345679-9")
    assert cuit.digito_verificador_valido()
    assert cuit.es_valido()


def test_dv_incorrecto_rechaza_variantes() -> None:
    assert not CUIT("27-12345678-1").es_valido()  # el dv correcto sería 0
    assert not CUIT("30-12345679-0").es_valido()  # el dv correcto sería 9


def test_formato_invalido_corta_el_verificador() -> None:
    """El cálculo del DV no lanza excepción ante caracteres no numéricos."""
    cuit = CUIT("30-1234567A-1")
    assert not cuit.formato_valido()
    assert not cuit.digito_verificador_valido()
