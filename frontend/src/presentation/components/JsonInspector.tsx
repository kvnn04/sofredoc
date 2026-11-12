/**
 * Inspector de JSON plegable (MOD-04 T-12, CU-03): "Ver JSON Estructurado
 * (Pydantic)" muestra `datos_extraidos` y `json_crudo_ia` en `<pre>` con
 * scroll y botón "Copiar" por sección (`navigator.clipboard`).
 */
import { useState } from "react";
import { Check, ChevronDown, ChevronRight, Copy } from "lucide-react";
import type { ResultadoAuditoria } from "../../domain/types";

interface Props {
  resultado: ResultadoAuditoria;
}

export function JsonInspector({ resultado }: Props) {
  const [abierto, setAbierto] = useState(false);
  return (
    <section className="rounded-xl border border-slate-200 bg-white shadow-sm">
      <button
        type="button"
        onClick={() => setAbierto((v) => !v)}
        aria-expanded={abierto}
        className="flex w-full items-center gap-2 px-4 py-3 text-left text-sm font-semibold text-slate-700 hover:bg-slate-50"
      >
        {abierto ? (
          <ChevronDown className="h-4 w-4 text-slate-500" aria-hidden />
        ) : (
          <ChevronRight className="h-4 w-4 text-slate-500" aria-hidden />
        )}
        Ver JSON Estructurado (Pydantic)
      </button>
      {abierto && (
        <div className="space-y-4 border-t border-slate-200 p-4">
          <SeccionJson titulo="Objeto Pydantic (datos_extraidos)" valor={resultado.datos_extraidos} />
          <SeccionJson titulo="JSON crudo IA (json_crudo_ia)" valor={resultado.json_crudo_ia} />
        </div>
      )}
    </section>
  );
}

function SeccionJson({ titulo, valor }: { titulo: string; valor: unknown }) {
  const [copiado, setCopiado] = useState(false);

  async function copiar() {
    try {
      await navigator.clipboard.writeText(JSON.stringify(valor, null, 2));
      setCopiado(true);
      window.setTimeout(() => setCopiado(false), 2000);
    } catch {
      setCopiado(false);
    }
  }

  return (
    <div>
      <div className="mb-1 flex items-center justify-between gap-2">
        <h3 className="text-xs font-semibold uppercase tracking-wide text-slate-500">{titulo}</h3>
        <button
          type="button"
          onClick={() => void copiar()}
          aria-label={`Copiar ${titulo} al portapapeles`}
          className="flex items-center gap-1 rounded border border-slate-300 px-2 py-1 text-xs text-slate-600 hover:bg-slate-50"
        >
          {copiado ? (
            <Check className="h-3 w-3 text-emerald-600" aria-hidden />
          ) : (
            <Copy className="h-3 w-3" aria-hidden />
          )}
          {copiado ? "¡Copiado!" : "Copiar"}
        </button>
      </div>
      {valor == null ? (
        <p className="text-sm text-slate-500">No disponible para esta auditoría.</p>
      ) : (
        <pre className="max-h-96 overflow-auto rounded-lg bg-slate-950 p-3 text-xs leading-relaxed text-slate-100">
          {JSON.stringify(valor, null, 2)}
        </pre>
      )}
    </div>
  );
}
