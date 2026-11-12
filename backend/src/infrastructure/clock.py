"""Reloj de negocio real: 'hoy' según la zona horaria America/Argentina/Buenos_Aires."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

ZONA_NEGOCIO = ZoneInfo("America/Argentina/Buenos_Aires")


class RelojSistema:
    """Implementa `ClockPort`: refleja el día local del operador aunque el server corra en UTC."""

    def hoy(self) -> date:
        return datetime.now(tz=ZONA_NEGOCIO).date()
