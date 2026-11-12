/**
 * Panel de historial (MOD-04 T-13, CU-04): tabla plegable (fecha, archivo,
 * estado con color, latencia ms) paginada simple; la fila seleccionada
 * re-carga la auditoría completa vía `obtenerAuditoria(id)`.
 */
import { ChevronDown, ChevronRight, History } from "lucide-react";
import type { ResumenAuditoria } from "../../domain/types";
import type { ErrorApi } from "../../infrastructure/apiClient";
import { formatoFechaHora } from "../formato";

const CHIP_ESTADO = {
  APROBADO: "bg-emerald-100 text-emerald-800",
  RECHAZADO: "bg-red-100 text-red-700",
  ERROR_EXTRACCION: "bg-amber-100 text-amber-800",
} as const;

interface Props {
  historial: ResumenAuditoria[];
  cargando: boolean;
  error: ErrorApi | null;
  offset: number;
  hayMas: boolean;
  abierto: boolean;
  idSeleccionado: string | null;
  onToggle: () => void;
  onSeleccionar: (id: string) => void;
  avanzar: () => void;
  retroceder: () => void;
}

export function Historial({
  historial,
  cargando,
  error,
  offset,
  hayMas,
  abierto,
  idSeleccionado,
  onToggle,
  onSeleccionar,
  avanzar,
  retroceder,
}: Props) {
  return (
    <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={abierto}
        className="flex w-full items-center gap-2 px-4 py-2.5 text-left text-sm font-semibold text-slate-700 hover:bg-slate-50"
      >
        {abierto ? (
          <ChevronDown className="h-4 w-4 text-slate-500" aria-hidden />
        ) : (
          <ChevronRight className="h-4 w-4 text-slate-500" aria-hidden />
        )}
        <History className="h-4 w-4 text-slate-500" aria-hidden />
        Historial de auditorías
        {historial.length > 0 && (
          <span className="rounded-full bg-slate-200 px-2 py-0.5 text-xs font-medium text-slate-600">
            {offset + 1}–{offset + historial.length}
          </span>
        )}
      </button>

      {abierto && (
        <div className="border-t border-slate-200">
          {error && <p className="px-4 py-3 text-sm text-red-700">{error.codigo}: {error.mensaje}</p>}
          {cargando && <p className="px-4 py-3 text-sm text-slate-500">Cargando historial…</p>}
          {!cargando && !error && historial.length === 0 && (
            <p className="px-4 py-3 text-sm text-slate-500">
              Sin auditorías todavía. Ejecutá un ejemplo para empezar.
            </p>
          )}
          {!cargando && historial.length > 0 && (
            <div className="max-h-64 overflow-auto">
              <table className="w-full text-left text-sm">
                <thead className="sticky top-0 bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    <th scope="col" className="px-4 py-2 font-medium">
                      Fecha
                    </th>
                    <th scope="col" className="px-4 py-2 font-medium">
                      Archivo
                    </th>
                    <th scope="col" className="px-4 py-2 font-medium">
                      Estado
                    </th>
                    <th scope="col" className="px-4 py-2 text-right font-medium">
                      Latencia
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {historial.map((fila) => (
                    <tr
                      key={fila.id}
                      tabIndex={0}
                      onClick={() => onSeleccionar(fila.id)}
                      onKeyDown={(evento) => {
                        if (evento.key === "Enter") onSeleccionar(fila.id);
                      }}
                      aria-label={`Ver detalle de la auditoría ${fila.id}`}
                      className={`cursor-pointer border-t border-slate-100 hover:bg-slate-50 focus:bg-sky-50 focus:outline-none ${
                        fila.id === idSeleccionado ? "bg-sky-50" : ""
                      }`}
                    >
                      <td className="px-4 py-2 text-xs text-slate-600">
                        {formatoFechaHora(fila.creado_en)}
                      </td>
                      <td className="px-4 py-2">
                        <span
                          className="block max-w-[18rem] truncate font-medium text-slate-800"
                          title={fila.nombre_archivo}
                        >
                          {fila.nombre_archivo}
                        </span>
                        <span className="font-mono text-[11px] text-slate-400">{fila.id}</span>
                      </td>
                      <td className="px-4 py-2">
                        <span
                          className={`rounded px-1.5 py-0.5 text-xs font-semibold ${CHIP_ESTADO[fila.estado]}`}
                        >
                          {fila.estado}
                        </span>
                      </td>
                      <td className="px-4 py-2 text-right font-mono text-xs text-slate-600">
                        {fila.tiempo_ejecucion_ms} ms
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          {!cargando && historial.length > 0 && (
            <div className="flex items-center justify-between border-t border-slate-200 px-4 py-2">
              <button
                type="button"
                onClick={retroceder}
                disabled={offset === 0}
                className="rounded px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
              >
                ← Anteriores
              </button>
              <button
                type="button"
                onClick={avanzar}
                disabled={!hayMas}
                className="rounded px-2 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-40"
              >
                Siguientes →
              </button>
            </div>
          )}
        </div>
      )}
    </section>
  );
}
