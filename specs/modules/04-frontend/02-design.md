# DESIGN-04: Frontend Clean Architecture — Diseño Técnico

> **Audiencia:** Ingenieros de Software, Agentes de IA.
> **Patrón:** Clean Architecture (Monolito FastAPI + React).

## 1. Arquitectura de Componentes y Capas

```text
frontend/src/
├── domain/
│   └── types.ts                  # Tipos del contrato API: ResultadoAuditoria, ReglaResultado,
│                                 # FacturaExtraida, ItemFactura, Ejemplo, ErrorApi
├── application/
│   ├── useAuditoria.ts           # Hook: auditar(ejemploId | file) → estado de auditoría
│   ├── useHistorial.ts           # Hook: cargar historial, refrescar tras auditoría
│   └── useEjemplos.ts            # Hook: cargar catálogo de ejemplos
├── infrastructure/
│   └── apiClient.ts              # fetch wrapper (base VITE_API_URL, errores tipados)
└── presentation/
    ├── components/
    │   ├── VisorPDF.tsx          # iframe/object del PDF (ejemplo vía API o blob de upload)
    │   ├── TablaDatos.tsx        # Datos extraídos + tabla de ítems
    │   ├── SemaforoReglas.tsx    # Badge global + lista R1..R5
    │   ├── JsonInspector.tsx     # JSON plegable + copiar
    │   ├── Historial.tsx         # Listado de auditorías previas
    │   ├── BarraSuperior.tsx     # Ejemplos rápidos + botón de subida + estado de conexión
    │   └── BannerError.tsx       # Error tipado de la API
    └── App.tsx                   # Layout de dos columnas + orquestación de hooks
```

## 2. Modelos de Datos y Esferas de Dominio

### Tipos de dominio (espejo exacto del contrato de MOD-03 — fuente única: la API)

```typescript
// frontend/src/domain/types.ts
export interface ItemFactura {
  descripcion: string;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
}

/** Línea de impuesto discriminada al pie (ADR-02-12). */
export interface ImpuestoDetalle {
  concepto: string;
  monto: number;
}

export interface FacturaExtraida {
  tipo_comprobante: "FACTURA" | "REMITO";
  letra_comprobante: string | null;   // ADR-02-11: ancla de extracción
  numero_comprobante: string | null;  // 'PPPPP-NNNNNNNN' con Punto de Venta (ADR-02-12)
  cuit_emisor: string;
  razon_social: string;
  fecha_emision: string;            // YYYY-MM-DD
  numero_orden_compra: string | null;
  items: ItemFactura[];
  detalle_impuestos: ImpuestoDetalle[]; // ADR-02-12: líneas del pie; impuestos = Σ montos
  impuestos: number;
  monto_total: number;
}

export interface ReglaResultado {
  codigo: "R0" | "R1" | "R2" | "R3" | "R4" | "R5";   // R0 = admisión (REMITO, ADR-05-08)
  nombre: string;
  aprobado: boolean;
  mensaje: string;
  codigo_error: string | null;
  detalles: Record<string, string> | null;           // p. ej. montos comparados por R3
}

export interface ResultadoAuditoria {
  id: string;
  estado: "APROBADO" | "RECHAZADO" | "ERROR_EXTRACCION";
  nombre_archivo: string;
  datos_extraidos: FacturaExtraida | null;
  reglas_evaluadas: ReglaResultado[];
  json_crudo_ia: unknown | null;
  tiempo_ejecucion_ms: number;
  latencia_extraccion_ms: number;
  latencia_reglas_ms: number;
  creado_en: string;
}

export interface Ejemplo {
  id: string;
  nombre: string;
  descripcion: string;
  archivo: string;
  resultado_esperado: "APROBADO" | "RECHAZADO";
}

export interface ErrorApi {
  error: { codigo: string; mensaje: string };
}
```

### Esquema de Base de Datos (SQLite)

No aplica (persistencia en backend, MOD-03).

## 3. Contratos de API (HTTP / JSON)

Consumidos vía `apiClient.ts` (espejo de MOD-03 §3):

| Función | HTTP | Notas |
| :--- | :--- | :--- |
| `auditarArchivo(file: File)` | `POST /auditar` | `FormData`; valida `file.type` y tamaño ≤ 5 MB antes de enviar |
| `auditarEjemplo(id: string)` | `POST /auditar` | descarga el PDF del ejemplo y lo re-envía como `file` (mismo contrato) |
| `listarEjemplos()` | `GET /ejemplos` | catálogo para la barra superior |
| `obtenerPdfEjemplo(id)` | `GET /ejemplos/{id}/pdf` | URL directa para el visor |
| `listarHistorial(limit, offset)` | `GET /historial` | refresca tras cada auditoría |
| `obtenerAuditoria(id)` | `GET /historial/{id}` | al seleccionar del historial |

Base URL: `import.meta.env.VITE_API_URL` (default `http://localhost:8000/api/v1`). Errores no-2xx se normalizan a `ErrorApi`.

## 4. Librerías y Dependencias Elegidas

- `react`, `typescript`, `vite`, `tailwindcss` (v4), `lucide-react` (iconos). **Sin** axios, sin router, sin state manager.
- Visor PDF: `<iframe>` (o `<object>` fallback) — no se agrega `pdf.js` en el MVP.

## 5. Diseño de Pantalla (Layout)

```text
┌──────────────────────────────────────────────────────────────────────────────┐
│ BarraSuperior: logo · [3 botones de ejemplo] · [Subir PDF] · modo extractor  │
├───────────────────────────────┬──────────────────────────────────────────────┤
│  VisorPDF (izq ~40%)          │  Panel de resultados (der ~60%)              │
│  ┌─────────────────────────┐  │  ┌────────────────────────────────────────┐  │
│  │ iframe PDF              │  │  │ Badge estado: APROBADO/RECHAZADO       │  │
│  │ (blob o /ejemplos/../pdf)│ │  │ tiempo_ejecucion_ms · id auditoría     │  │
│  └─────────────────────────┘  │  ├────────────────────────────────────────┤  │
│                               │  │ SemaforoReglas: R1..R5 ✅/❌ + mensajes │  │
│                               │  ├────────────────────────────────────────┤  │
│                               │  │ TablaDatos: cabecera + ítems + totales │  │
│                               │  ├────────────────────────────────────────┤  │
│                               │  │ [Ver JSON Estructurado (Pydantic)] ▸   │  │
│                               │  │ JsonInspector plegable + copiar        │  │
│                               │  └────────────────────────────────────────┘  │
├───────────────────────────────┴──────────────────────────────────────────────┤
│ Historial (pestaña inferior desplegable o panel colapsable)                  │
└──────────────────────────────────────────────────────────────────────────────┘
```

- **Colores semáforo:** aprobado `bg-emerald-600`/texto blanco; rechazado `bg-red-600`; pendiente/inicial `bg-slate-300`. Badge global con `CheckCircle2` / `XCircle` y **desglose de latencia** en el encabezado: `IA 1280 ms · reglas 3 ms · total 1420 ms`.
- **SemaforoReglas:** una fila por regla: código (chip `R1`), nombre, mensaje y `codigo_error` en rojo monospace si falla.
- **TablaDatos:** cabecera (tipo, número, CUIT, razón social, fecha, OC, impuestos — suma de `detalle_impuestos`, ADR-02-12 —, total) + tabla de ítems (descripción, cantidad, precio unitario, subtotal) + fila total resaltada; montos formateados `es-AR` (`$ 384.000,00`). El desglose línea a línea queda visible en el JsonInspector dentro de `datos_extraidos`.
- **Estados:** `idle` (empty-state con instrucciones y flecha a los ejemplos), `loading` (skeleton + "Auditando documento…" y botones deshabilitados), `resultado`, `error` (BannerError con `codigo`/`mensaje`).
- **Accesibilidad mínima:** botones reales con `aria-label`, foco visible, contraste AA.
