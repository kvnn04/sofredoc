"""Puerto de salida: reloj de negocio inyectable (R5 usa 'hoy')."""

from datetime import date
from typing import Protocol


class ClockPort(Protocol):
    """Contrato de reloj: 'hoy' en la zona de negocio (America/Argentina/Buenos_Aires)."""

    def hoy(self) -> date: ...
