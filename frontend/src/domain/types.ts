/**
 * Espejo exacto del contrato API de MOD-03 (fuente única: la API).
 * DESIGN-04 §2. Los montos llegan como número con 2 decimales (la API
 * serializa Decimal → float); las fechas en ISO 8601.
 */

export interface HealthResponse {
  status: string;
  version: string;
  extractor_mode: string;
}

/** Ítem de factura tal como lo extrajo la IA (no se corrige en el cliente). */
export interface ItemFactura {
  descripcion: string;
  cantidad: number;
  precio_unitario: number;
  subtotal: number;
}

/** `FacturaExtraida` serializada por la API dentro de `datos_extraidos`. */
export interface FacturaExtraida {
  tipo_comprobante: "FACTURA" | "REMITO";
  numero_comprobante: string | null;
  cuit_emisor: string;
  razon_social: string;
  /** YYYY-MM-DD (ISO 8601, convención global). */
  fecha_emision: string;
  numero_orden_compra: string | null;
  items: ItemFactura[];
  impuestos: number;
  monto_total: number;
}

/** Fila del semáforo (incluye R0 de admisión cuando el comprobante es REMITO). */
export interface ReglaResultado {
  codigo: "R0" | "R1" | "R2" | "R3" | "R4" | "R5";
  nombre: string;
  aprobado: boolean;
  mensaje: string;
  codigo_error: string | null;
  detalles: Record<string, string> | null;
}

/** Respuesta de `POST /auditar` y de `GET /historial/{id}`. */
export interface ResultadoAuditoria {
  id: string;
  estado: "APROBADO" | "RECHAZADO" | "ERROR_EXTRACCION";
  nombre_archivo: string;
  cuit_emisor: string | null;
  monto_total: number | null;
  datos_extraidos: FacturaExtraida | null;
  reglas_evaluadas: ReglaResultado[];
  json_crudo_ia: Record<string, unknown> | null;
  tiempo_ejecucion_ms: number;
  latencia_extraccion_ms: number;
  latencia_reglas_ms: number;
  creado_en: string;
}

/** Ítem del listado `GET /historial`: igual al detalle sin `json_crudo_ia`. */
export type ResumenAuditoria = Omit<ResultadoAuditoria, "json_crudo_ia">;

/** Entrada del catálogo de ejemplos (`GET /ejemplos`). */
export interface Ejemplo {
  id: string;
  nombre: string;
  descripcion: string;
  resultado_esperado: string;
  /** Ruta relativa del PDF servido por la API (`/api/v1/ejemplos/{id}/pdf`). */
  url_pdf: string;
}

/** Cuerpo de error tipado de la API (413/422/502/404, RN-3-02). */
export interface CuerpoError {
  error: { codigo: string; mensaje: string };
}
