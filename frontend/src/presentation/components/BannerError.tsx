/**
 * Banner de error tipado de la API (MOD-04 T-14, CU-05): muestra `codigo` +
 * `mensaje` para 413/422/502 (y red caída) sin destruir el estado previo de
 * la pantalla — el componente que lo contiene decide dónde renderizarlo.
 */
import { AlertTriangle, X } from "lucide-react";
import type { ErrorApi } from "../../infrastructure/apiClient";

interface Props {
  error: ErrorApi | null;
  /** Botón opcional de acción (ej. "Reintentar"). */
  accionEtiqueta?: string;
  onAccion?: () => void;
  onCerrar?: () => void;
}

export function BannerError({ error, accionEtiqueta, onAccion, onCerrar }: Props) {
  if (!error) return null;
  return (
    <div
      role="alert"
      className="flex items-start gap-3 rounded-lg border border-red-300 bg-red-50 px-3 py-2.5 text-sm text-red-800"
    >
      <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-red-600" aria-hidden />
      <div className="min-w-0 flex-1">
        <span className="mr-2 rounded bg-red-100 px-1.5 py-0.5 font-mono text-xs font-semibold text-red-700">
          {error.codigo}
        </span>
        <span>{error.mensaje}</span>
        {accionEtiqueta && onAccion && (
          <button
            type="button"
            onClick={onAccion}
            className="ml-3 font-semibold text-red-700 underline hover:text-red-900"
          >
            {accionEtiqueta}
          </button>
        )}
      </div>
      {onCerrar && (
        <button
          type="button"
          onClick={onCerrar}
          aria-label="Cerrar el mensaje de error"
          className="shrink-0 rounded p-1 text-red-600 hover:bg-red-100 hover:text-red-800"
        >
          <X className="h-4 w-4" aria-hidden />
        </button>
      )}
    </div>
  );
}
