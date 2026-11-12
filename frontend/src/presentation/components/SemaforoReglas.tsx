/**
 * Semáforo de auditoría (MOD-04 T-10): badge global APROBADO/RECHAZADO (o
 * ERROR DE EXTRACCIÓN, visible al recargar filas del historial), desglose de
 * latencia por etapa (IA / reglas / total), id de auditoría y una fila por
 * regla con chip, nombre, mensaje y `codigo_error` en rojo monospace.
 * Solo renderiza lo que devuelve la API: no re-evalúa reglas (RN-4-01).
 */
import { AlertTriangle, CheckCircle2, XCircle } from "lucide-react";
import type { ReglaResultado, ResultadoAuditoria } from "../../domain/types";

interface Props {
  resultado: ResultadoAuditoria;
}

const FONDO_BADGE = {
  APROBADO: "bg-emerald-600",
  RECHAZADO: "bg-red-600",
  ERROR_EXTRACCION: "bg-amber-500",
} as const;

const ETIQUETA_BADGE = {
  APROBADO: "APROBADO",
  RECHAZADO: "RECHAZADO",
  ERROR_EXTRACCION: "ERROR DE EXTRACCIÓN",
} as const;

export function SemaforoReglas({ resultado }: Props) {
  const estado = resultado.estado;
  return (
    <section
      aria-label="Semáforo de auditoría"
      className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <span
            className={`flex items-center gap-2 rounded-full px-4 py-1.5 text-sm font-bold text-white ${FONDO_BADGE[estado]}`}
          >
            {estado === "APROBADO" ? (
              <CheckCircle2 className="h-4 w-4" aria-hidden />
            ) : estado === "RECHAZADO" ? (
              <XCircle className="h-4 w-4" aria-hidden />
            ) : (
              <AlertTriangle className="h-4 w-4" aria-hidden />
            )}
            {ETIQUETA_BADGE[estado]}
          </span>
          <span
            className="max-w-[16rem] truncate text-xs text-slate-500"
            title={resultado.nombre_archivo}
          >
            {resultado.nombre_archivo}
          </span>
        </div>
        <div className="text-right">
          <p className="font-mono text-xs text-slate-500" title="Identificador de la auditoría">
            {resultado.id}
          </p>
          {/* Desglose de latencia por etapa (convención global, decisión firme 6). */}
          <p className="text-xs text-slate-500">
            IA {resultado.latencia_extraccion_ms} ms · reglas {resultado.latencia_reglas_ms} ms ·{" "}
            <strong className="text-slate-700">total {resultado.tiempo_ejecucion_ms} ms</strong>
          </p>
        </div>
      </div>

      {resultado.reglas_evaluadas.length > 0 ? (
        <ul className="mt-3 space-y-2">
          {resultado.reglas_evaluadas.map((regla) => (
            <FilaRegla key={regla.codigo} regla={regla} />
          ))}
        </ul>
      ) : (
        <p className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-sm text-amber-800">
          No se evaluaron reglas: la extracción con IA falló (trazabilidad en el historial).
        </p>
      )}
    </section>
  );
}

function FilaRegla({ regla }: { regla: ReglaResultado }) {
  return (
    <li className="flex items-start gap-3 rounded-lg border border-slate-200 px-3 py-2">
      {regla.aprobado ? (
        <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-600" aria-hidden />
      ) : (
        <XCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-600" aria-hidden />
      )}
      <div className="min-w-0 flex-1">
        <div className="flex flex-wrap items-center gap-2">
          <span
            className={`rounded px-1.5 py-0.5 font-mono text-xs font-bold ${
              regla.aprobado ? "bg-emerald-50 text-emerald-700" : "bg-red-100 text-red-700"
            }`}
          >
            {regla.codigo}
          </span>
          <span className="text-sm font-medium text-slate-800">{regla.nombre}</span>
          {regla.codigo_error && (
            <span className="font-mono text-xs font-semibold text-red-600" title={regla.codigo_error}>
              {regla.codigo_error}
            </span>
          )}
        </div>
        <p className="mt-0.5 text-sm text-slate-600">{regla.mensaje}</p>
      </div>
    </li>
  );
}
