/**
 * Formateo `es-AR` (T-15): montos `$ 384.000,00`, cantidades y fechas.
 * La fecha de emisión (`YYYY-MM-DD`) se formatea por partes para evitar
 * desplazamientos de zona horaria; los timestamps UTC usan `Intl`.
 */

const MONEDA = new Intl.NumberFormat("es-AR", {
  style: "currency",
  currency: "ARS",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const CANTIDAD = new Intl.NumberFormat("es-AR", { maximumFractionDigits: 2 });

const FECHA_HORA = new Intl.DateTimeFormat("es-AR", {
  dateStyle: "short",
  timeStyle: "medium",
});

/** Monto en ARS con 2 decimales (convención global de specs/README.md). */
export function formatoArs(valor: number): string {
  return MONEDA.format(valor);
}

/** Cantidad de un ítem (admite decimales, ej. 2.5 horas). */
export function formatoCantidad(valor: number): string {
  return CANTIDAD.format(valor);
}

/** `YYYY-MM-DD` → `DD/MM/YYYY` sin pasar por `Date` (no hay TZ que corra el día). */
export function formatoFecha(iso: string): string {
  const partes = iso.split("-");
  if (partes.length !== 3) return iso;
  const [anio, mes, dia] = partes;
  return `${dia}/${mes}/${anio}`;
}

/** Timestamp ISO UTC → fecha y hora en `es-AR` para el historial. */
export function formatoFechaHora(iso: string): string {
  const fecha = new Date(iso);
  if (Number.isNaN(fecha.getTime())) return iso;
  return FECHA_HORA.format(fecha);
}
