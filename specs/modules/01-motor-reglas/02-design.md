# DESIGN-01: Dominio y Motor de Reglas — Diseño Técnico

> **Audiencia:** Ingenieros de Software, Agentes de IA.
> **Patrón:** Clean Architecture (Monolito FastAPI + React).

## 1. Arquitectura de Componentes y Capas

Este módulo vive **íntegramente en `backend/src/domain/`** (Python puro, sin I/O salvo el adaptador de padrón en `infrastructure/`):

```text
backend/src/domain/
├── models.py                  # FacturaExtraida, ItemFactura, ReglaResultado, ResultadoAuditoria
├── value_objects/
│   └── cuit.py                # Value Object CUIT (normalización + módulo 11)
├── rules/
│   ├── base.py                # Protocol Regla + ContextoAuditoria
│   ├── r1_cuit.py ... r5_vigencia.py
│   └── engine.py              # Evaluador agregado (admisión R0 + R1→R5, estado global)
└── ports/
    ├── padron_port.py         # PadronProveedoresPort
    └── clock_port.py          # ClockPort (hoy inyectable)
```

```text
backend/src/infrastructure/padron/
└── json_padron.py             # Adaptador que lee data/proveedores.json
```

## 2. Modelos de Datos y Esferas de Dominio

### Entidades y Value Objects (Python / Pydantic)

```python
# backend/src/domain/models.py
from datetime import date
from decimal import Decimal
from typing import Literal, Optional
from pydantic import BaseModel, Field

class ItemFactura(BaseModel):
    descripcion: str = Field(min_length=1)
    cantidad: Decimal = Field(gt=0)
    precio_unitario: Decimal = Field(ge=0)
    subtotal: Decimal = Field(ge=0)

class FacturaExtraida(BaseModel):
    tipo_comprobante: Literal["FACTURA", "REMITO"]
    numero_comprobante: Optional[str] = None
    cuit_emisor: str                                  # normalizado por el VO CUIT en las reglas
    razon_social: str = Field(min_length=1)
    fecha_emision: date
    numero_orden_compra: Optional[str] = None
    items: list[ItemFactura] = Field(min_length=1)
    impuestos: Decimal = Decimal("0.00")
    monto_total: Decimal = Field(gt=0)

class ReglaResultado(BaseModel):
    codigo: Literal["R0", "R1", "R2", "R3", "R4", "R5"]
    nombre: str
    aprobado: bool
    mensaje: str                                      # legible para el operador
    codigo_error: Optional[str] = None                # ej. DISCREPANCIA_CONTABLE
    detalles: Optional[dict] = None                   # ej. {"calculado": "270000.00", "declarado": "285000.00"}

class ResultadoAuditoria(BaseModel):
    estado: Literal["APROBADO", "RECHAZADO"]
    reglas: list[ReglaResultado]

    @classmethod
    def desde_reglas(cls, reglas: list["ReglaResultado"]) -> "ResultadoAuditoria":
        estado = "APROBADO" if all(r.aprobado for r in reglas) else "RECHAZADO"
        return cls(estado=estado, reglas=reglas)
```

> **Nota de dinero:** el dominio usa `Decimal` (exactitud contable). La serialización a JSON (capa presentación, MOD-03) convierte montos a número con 2 decimales.

### Value Object CUIT — Algoritmo Módulo 11 (R1)

```python
# backend/src/domain/value_objects/cuit.py
PESOS = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

class CUIT:
    """Normaliza y valida CUIT argentino (módulo 11)."""

    def __init__(self, valor: str) -> None:
        self.bruto = valor.strip()
        self.digitos = self.bruto.replace("-", "")

    def formato_valido(self) -> bool:
        return len(self.digitos) == 11 and self.digitos.isdigit()

    def digito_verificador_valido(self) -> bool:
        suma = sum(int(d) * p for d, p in zip(self.digitos[:10], PESOS))
        resto = suma % 11
        dv = 11 - resto
        if dv == 11:
            dv = 0
        elif dv == 10:
            dv = 9
        return dv == int(self.digitos[10])

    def es_valido(self) -> bool:
        return self.formato_valido() and self.digito_verificador_valido()
```

### Interfaz de Regla y Contexto

```python
# backend/src/domain/rules/base.py
from dataclasses import dataclass
from typing import Protocol, Optional
from src.domain.models import FacturaExtraida, ReglaResultado

@dataclass(frozen=True)
class ContextoAuditoria:
    hoy: date                                  # inyectado por ClockPort
    proveedor: Optional["Proveedor"] = None    # lookup de padrón (None si no existe)

class Proveedor:
    cuit: str
    razon_social: str
    activo: bool

class Regla(Protocol):
    codigo: str
    nombre: str
    def evaluar(self, factura: FacturaExtraida, ctx: ContextoAuditoria) -> ReglaResultado: ...
```

> **Reloj del sistema (R5):** el `RelojSistema` (adaptador de `ClockPort`) resuelve "hoy" en la zona horaria `America/Argentina/Buenos_Aires` (decisión 2026-11-12), de modo que la vigencia refleja el día local del operador aunque el servidor corra en UTC.

### Lógica de cada regla (condiciones exactas)

| Regla | Condición de aprobación | Mensaje OK | Mensaje de fallo (ejemplo) |
| :--- | :--- | :--- | :--- |
| **R0** (admisión) | `tipo_comprobante == "FACTURA"`; un REMITO corta la evaluación (R1–R5 no corren) | *n/a* | `Comprobante tipo REMITO: fuera de alcance del MVP (solo se auditan facturas).` |
| **R1** | `CUIT.es_valido()` | `CUIT válido (dígito verificador correcto).` | `CUIT con dígito verificador incorrecto o formato inválido.` |
| **R2** | `ctx.proveedor is not None and ctx.proveedor.activo` | `Proveedor activo en el padrón.` | `El CUIT no se encuentra registrado o activo en el padrón de proveedores.` |
| **R3** | `abs(calculado - monto_total) <= Decimal("1.00")` donde `calculado = Σ(cantidad × precio_unitario) + impuestos` | `Suma de ítems + impuestos coincide con el total.` | `La suma de ítems + impuestos ($270.000,00) no coincide con el total declarado ($285.000,00).` |
| **R4** | `monto_total <= 500000` **o** `numero_orden_compra` no vacío | `OC presente.` / `Monto bajo el tope, OC no requerida.` | `Comprobante de $725.000 supera el tope de $500.000 sin Orden de Compra.` |
| **R5** | `fecha_emision <= ctx.hoy` y `(ctx.hoy - fecha_emision).days <= 60` | `Fecha de emisión dentro de la vigencia (60 días).` | `Comprobante vencido (emitido hace 75 días; tope 60).` / `Fecha de emisión futura.` |

### Padrón simulado (adaptador `infrastructure/padron/json_padron.py`)

```json
// backend/data/proveedores.json
[
  { "cuit": "30-12345678-1", "razon_social": "Distribuidora Andina S.A.",   "activo": true },
  { "cuit": "30-71234567-1", "razon_social": "Comercial Austral SRL",       "activo": true },
  { "cuit": "20-12345678-6", "razon_social": "Servicios Técnicos SD S.A.",  "activo": true },
  { "cuit": "20-87654321-5", "razon_social": "Proveedor Baja SRL",          "activo": false }
]
```

El adaptador carga el JSON una vez (cache en memoria) y expone `buscar(cuit_normalizado) -> Optional[Proveedor]`. CUITs de referencia **válidos según módulo 11**: `30-12345678-1`, `30-71234567-1`, `20-12345678-6`, `20-87654321-5`. CUIT de referencia **inválido** (DV incorrecto): `30-12345678-9`.

### Esquema de Base de Datos (SQLite)

No aplica en este módulo (persistencia en MOD-03).

## 3. Contratos de API (HTTP / JSON)

No aplica en este módulo (los resultados exponen por la API de MOD-03; el contrato de `ReglaResultado` JSON es el definido en §2).

## 4. Librerías y Dependencias Elegidas

- Solo stdlib + `pydantic` (modelos). **Sin** dependencias de cálculo (no `pandas`, no `moneyed`): `Decimal` nativo alcanza.
- Tests: `pytest`. El "hoy" se inyecta como `date` fija en cada test (sin `freezegun`).
