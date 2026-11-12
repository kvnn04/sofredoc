/**
 * Cliente HTTP de la API (MOD-04 T-02/T-03, DESIGN-04 §3).
 *
 * - Base URL desde `VITE_API_URL`; si está vacía se usa el proxy de desarrollo
 *   de Vite (`/api/v1` → `http://localhost:8000`, configurado en MOD-00 T-07).
 * - Los errores no-2xx (`{"error": {codigo, mensaje}}`) se normalizan a
 *   `ErrorApi`; las validaciones client-side (PDF válido ≤ 5 MB) también
 *   levantan `ErrorApi` para que la UI las trate igual (RN-4-03, CU-05).
 */
import type { CuerpoError, Ejemplo, ResumenAuditoria, ResultadoAuditoria } from "../domain/types";

const BASE: string = import.meta.env.VITE_API_URL || "/api/v1";

/** Tope de subida validado en el cliente (RN-4-03; el servidor lo re-confirma). */
export const MAX_PDF_MB = 5;

const BYTES_POR_MB = 1024 * 1024;

/** Error tipado de la API o de una validación client-side (banner CU-05). */
export class ErrorApi extends Error {
  codigo: string;
  mensaje: string;

  constructor(codigo: string, mensaje: string) {
    super(mensaje);
    this.name = "ErrorApi";
    this.codigo = codigo;
    this.mensaje = mensaje;
  }
}

/** Convierte cualquier excepción en `ErrorApi` (red caída, respuesta no-JSON…). */
export function aErrorApi(error: unknown): ErrorApi {
  if (error instanceof ErrorApi) return error;
  return new ErrorApi(
    "ERROR_INESPERADO",
    error instanceof Error ? error.message : "Error inesperado del cliente.",
  );
}

/** Normaliza la respuesta del backend al error tipado del cuerpo `{"error": …}`. */
async function errorDeRespuesta(response: Response): Promise<ErrorApi> {
  try {
    const cuerpo = (await response.json()) as CuerpoError;
    if (cuerpo?.error?.codigo && cuerpo?.error?.mensaje) {
      return new ErrorApi(cuerpo.error.codigo, cuerpo.error.mensaje);
    }
  } catch {
    // cuerpo no JSON: se cae al genérico
  }
  return new ErrorApi("ERROR_HTTP", `El backend respondió el error HTTP ${response.status}.`);
}

async function apiFetch<T>(ruta: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE}${ruta}`, init);
  } catch {
    throw new ErrorApi(
      "ERROR_RED",
      "No se pudo conectar con el backend. ¿Está corriendo en el puerto 8000?",
    );
  }
  if (!response.ok) {
    throw await errorDeRespuesta(response);
  }
  return (await response.json()) as T;
}

/** URL directa del PDF de un ejemplo, servida por la API (para el iframe). */
export function obtenerPdfEjemplo(id: string): string {
  return `${BASE}/ejemplos/${encodeURIComponent(id)}/pdf`;
}

/** Validación client-side de RN-4-03: PDF válido y ≤ 5 MB (feedback inmediato). */
export function validarPdf(archivo: File): void {
  const esPdf =
    archivo.type === "application/pdf" || archivo.name.toLowerCase().endsWith(".pdf");
  if (!esPdf) {
    throw new ErrorApi(
      "PDF_INVALIDO",
      "El archivo debe ser un PDF (extensión .pdf o content-type application/pdf).",
    );
  }
  if (archivo.size > MAX_PDF_MB * BYTES_POR_MB) {
    throw new ErrorApi("ARCHIVO_MUY_GRANDE", `El archivo supera el tope de ${MAX_PDF_MB} MB.`);
  }
}

/** `POST /auditar`: sube el PDF propio (mismo contrato para ejemplos y uploads). */
export async function auditarArchivo(archivo: File): Promise<ResultadoAuditoria> {
  validarPdf(archivo);
  const form = new FormData();
  form.append("file", archivo);
  return apiFetch<ResultadoAuditoria>("/auditar", { method: "POST", body: form });
}

/** T-03: descarga `GET /ejemplos/{id}/pdf` como blob → File → `POST /auditar`. */
export async function auditarEjemplo(id: string): Promise<ResultadoAuditoria> {
  let respuesta: Response;
  try {
    respuesta = await fetch(obtenerPdfEjemplo(id));
  } catch {
    throw new ErrorApi(
      "ERROR_RED",
      "No se pudo descargar el PDF del ejemplo. ¿Está corriendo el backend en el puerto 8000?",
    );
  }
  if (!respuesta.ok) {
    throw await errorDeRespuesta(respuesta);
  }
  const blob = await respuesta.blob();
  const archivo = new File([blob], `${id}.pdf`, { type: "application/pdf" });
  return auditarArchivo(archivo);
}

/** `GET /ejemplos`: catálogo de los 3 ejemplos pre-cargados. */
export async function listarEjemplos(): Promise<Ejemplo[]> {
  return apiFetch<Ejemplo[]>("/ejemplos");
}

/** `GET /historial?limit&offset`: listado paginado sin `json_crudo_ia` (CU-04). */
export async function listarHistorial(limit = 20, offset = 0): Promise<ResumenAuditoria[]> {
  return apiFetch<ResumenAuditoria[]>(`/historial?limit=${limit}&offset=${offset}`);
}

/** `GET /historial/{id}`: detalle completo de una auditoría (con JSON crudo). */
export async function obtenerAuditoria(id: string): Promise<ResultadoAuditoria> {
  return apiFetch<ResultadoAuditoria>(`/historial/${encodeURIComponent(id)}`);
}
