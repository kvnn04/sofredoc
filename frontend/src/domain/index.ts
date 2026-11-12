/**
 * Modelos e interfaces TS del contrato API (espejo de `backend/src/domain/`).
 * MOD-03/MOD-04 agregan los tipos reales (ResultadoAuditoria, Ejemplo, ...).
 */

export interface HealthResponse {
  status: string;
  version: string;
  extractor_mode: string;
}
