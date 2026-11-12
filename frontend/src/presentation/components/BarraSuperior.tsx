/**
 * Barra superior (MOD-04 T-08): título, botones de los 3 ejemplos (nombre +
 * chip del resultado esperado) y botón "Subir PDF" con input oculto
 * `accept="application/pdf"`. La validación client-side de 5 MB/ formato la
 * hace `auditarArchivo` (feedback inmediato como BannerError, CU-05).
 * Durante la auditoría los botones se deshabilitan (sin doble submit).
 */
import { useRef, type ChangeEvent } from "react";
import { Loader2, ShieldCheck, Upload } from "lucide-react";
import type { Ejemplo } from "../../domain/types";

interface Props {
  ejemplos: Ejemplo[];
  cargandoEjemplos: boolean;
  auditando: boolean;
  alAuditar: (destino: string | File) => void;
}

export function BarraSuperior({ ejemplos, cargandoEjemplos, auditando, alAuditar }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);

  function alElegirArchivo(evento: ChangeEvent<HTMLInputElement>) {
    const archivo = evento.target.files?.[0];
    evento.target.value = ""; // permite re-subir el mismo archivo
    if (archivo) {
      void alAuditar(archivo);
    }
  }

  return (
    <header className="border-b border-slate-200 bg-white px-4 py-3 shadow-sm">
      <div className="mx-auto flex w-full max-w-[1600px] flex-wrap items-center gap-3">
        <h1 className="flex items-center gap-2 text-lg font-bold text-slate-900">
          <ShieldCheck className="h-6 w-6 text-emerald-600" aria-hidden />
          SofreDoc Validator
        </h1>

        <nav aria-label="Ejemplos pre-cargados" className="flex flex-wrap items-center gap-2">
          {cargandoEjemplos && (
            <span className="flex items-center gap-1 text-xs text-slate-500">
              <Loader2 className="h-3 w-3 animate-spin" aria-hidden />
              Cargando ejemplos…
            </span>
          )}
          {ejemplos.map((ejemplo) => (
            <button
              key={ejemplo.id}
              type="button"
              disabled={auditando}
              title={ejemplo.descripcion}
              aria-label={`Auditar ejemplo: ${ejemplo.nombre}`}
              onClick={() => alAuditar(ejemplo.id)}
              className="flex flex-col items-start rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-left text-xs font-medium text-slate-700 transition hover:border-emerald-500 hover:bg-emerald-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <span>{ejemplo.nombre}</span>
              <span className={`text-[10px] font-bold uppercase ${chipClase(ejemplo.resultado_esperado)}`}>
                {chipTexto(ejemplo.resultado_esperado)}
              </span>
            </button>
          ))}
        </nav>

        <div className="ml-auto flex items-center gap-2">
          <input
            ref={inputRef}
            type="file"
            accept="application/pdf"
            className="hidden"
            onChange={alElegirArchivo}
          />
          <button
            type="button"
            disabled={auditando}
            aria-label="Subir un PDF propio (máximo 5 MB)"
            onClick={() => inputRef.current?.click()}
            className="flex items-center gap-2 rounded-lg bg-slate-900 px-3 py-2 text-sm font-semibold text-white transition hover:bg-slate-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {auditando ? (
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
            ) : (
              <Upload className="h-4 w-4" aria-hidden />
            )}
            {auditando ? "Auditando…" : "Subir PDF"}
          </button>
        </div>
      </div>
    </header>
  );
}

/** Color del chip según el resultado esperado del catálogo (APROBADO/RECHAZADO…). */
function chipClase(esperado: string): string {
  if (esperado.startsWith("APROBADO")) return "text-emerald-600";
  if (esperado.startsWith("RECHAZADO")) return "text-red-500";
  return "text-slate-500";
}

/** El catálogo trae "RECHAZADO (R3: DISCREPANCIA_CONTABLE)": chip solo con la palabra clave. */
function chipTexto(esperado: string): string {
  const palabra = esperado.split(" ")[0] ?? esperado;
  if (palabra === "APROBADO" || palabra === "RECHAZADO") return palabra;
  return esperado;
}
