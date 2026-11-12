"""Value Object CUIT: normalización de guiones y dígito verificador Módulo 11 (AFIP)."""

PESOS = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]


class CUIT:
    """Normaliza y valida un CUIT argentino (módulo 11).

    Acepta formatos `30-12345678-1` y `30123456781` (se normalizan);
    la variante del algoritmo es dv=11 -> 0 y dv=10 -> 9 (ADR 2026-11-12).
    """

    def __init__(self, valor: str) -> None:
        self.bruto = valor.strip()
        self.digitos = self.bruto.replace("-", "")

    def formato_valido(self) -> bool:
        """11 dígitos numéricos luego de quitar guiones."""
        return len(self.digitos) == 11 and self.digitos.isdigit()

    def digito_verificador_valido(self) -> bool:
        """Pondera los primeros 10 dígitos y compara contra el dígito 11."""
        if not self.formato_valido():
            return False
        suma = sum(int(d) * p for d, p in zip(self.digitos[:10], PESOS, strict=False))
        resto = suma % 11
        dv = 11 - resto
        if dv == 11:
            dv = 0
        elif dv == 10:
            dv = 9
        return dv == int(self.digitos[10])

    def es_valido(self) -> bool:
        return self.formato_valido() and self.digito_verificador_valido()
