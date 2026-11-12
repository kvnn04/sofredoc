/**
 * Cliente HTTP base para la API del backend.
 * Convención (T-07): si `VITE_API_URL` está vacío, se usa el proxy de
 * desarrollo de Vite (`/api` → http://localhost:8000). Los endpoints reales
 * se agregan en MOD-03/MOD-04.
 */
const API_URL = import.meta.env.VITE_API_URL ?? "";

export async function apiFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${path}`, init);
  if (!response.ok) {
    const detalle = await response.text();
    throw new Error(`Error HTTP ${response.status}: ${detalle}`);
  }
  return (await response.json()) as T;
}
