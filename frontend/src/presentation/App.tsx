/**
 * Pantalla dividida (MOD-04 T-07, DESIGN-04 §5): visor PDF (~40%) a la
 * izquierda y panel de resultados (~60%) a la derecha, con la barra superior
 * y el panel de historial plegable al pie. Maquina de estados visual:
 * empty-state → skeleton de carga → resultado (o banner de error encima).
 * Single Page App de una pantalla: sin router ni store global (RN-4-02).
 */
import { useCallback, useState } from "react";
import { FileText, Loader2, MousePointerClick } from "lucide-react";
import { useAuditoria, useEjemplos, useHistorial } from "../application";
import { BannerError } from "./components/BannerError";
import { BarraSuperior } from "./components/BarraSuperior";
import { Historial } from "./components/Historial";
import { JsonInspector } from "./components/JsonInspector";
import { SemaforoReglas } from "./components/SemaforoReglas";
import { TablaDatos } from "./components/TablaDatos";
import { VisorPDF } from "./components/VisorPDF";

export default function App() {
  const { ejemplos, cargando: cargandoEjemplos, error: errorEjemplos, recargar } = useEjemplos();
  const {
    historial,
    cargando: cargandoHistorial,
    error: errorHistorial,
    offset,
    hayMas,
    refrescar,
    avanzar,
    retroceder,
  } = useHistorial();
  const { estado, resultado, pdfUrl, error, auditar, verDetalle } = useAuditoria();
  const [idSeleccionado, setIdSeleccionado] = useState<string | null>(null);
  const [historialAbierto, setHistorialAbierto] = useState(false);

  /** Audita un ejemplo o archivo y, si salió bien, refresca el historial (T-06). */
  const manejarAuditoria = useCallback(
    async (destino: string | File) => {
      const registro = await auditar(destino);
      if (registro) {
        setIdSeleccionado(registro.id);
        void refrescar();
      }
    },
    [auditar, refrescar],
  );

  /** CU-04: al seleccionar una fila del historial se re-carga en el panel principal. */
  const manejarSeleccion = useCallback(
    async (id: string) => {
      setIdSeleccionado(id);
      setHistorialAbierto(false);
      await verDetalle(id);
    },
    [verDetalle],
  );

  return (
    <div className="flex h-screen flex-col bg-slate-100 text-slate-900">
      <BarraSuperior
        ejemplos={ejemplos}
        cargandoEjemplos={cargandoEjemplos}
        auditando={estado === "loading"}
        alAuditar={(destino) => void manejarAuditoria(destino)}
      />

      {errorEjemplos && (
        <div className="mx-auto w-full max-w-[1600px] px-4 pt-3">
          <BannerError error={errorEjemplos} accionEtiqueta="Reintentar" onAccion={recargar} />
        </div>
      )}

      <main className="mx-auto flex w-full max-w-[1600px] min-h-0 flex-1 flex-col gap-3 p-4">
        {/* Dos columnas: visor 40% / resultados 60% (se apilan bajo 1024px). */}
        <div className="grid min-h-0 flex-1 grid-cols-1 gap-3 lg:grid-cols-[2fr_3fr]">
          <div className="min-h-0 lg:h-full">
            <VisorPDF pdfUrl={pdfUrl} nombreArchivo={resultado?.nombre_archivo ?? null} />
          </div>

          <div className="min-h-0 space-y-3 overflow-y-auto lg:h-full" aria-live="polite">
            {error && <BannerError error={error} />}
            {estado === "loading" ? (
              <EsqueletoCarga />
            ) : resultado ? (
              <>
                <SemaforoReglas resultado={resultado} />
                <TablaDatos datos={resultado.datos_extraidos} />
                <JsonInspector resultado={resultado} />
              </>
            ) : (
              <EstadoInicial />
            )}
          </div>
        </div>

        <Historial
          historial={historial}
          cargando={cargandoHistorial}
          error={errorHistorial}
          offset={offset}
          hayMas={hayMas}
          abierto={historialAbierto}
          idSeleccionado={idSeleccionado}
          onToggle={() => setHistorialAbierto((v) => !v)}
          onSeleccionar={(id) => void manejarSeleccion(id)}
          avanzar={avanzar}
          retroceder={retroceder}
        />
      </main>
    </div>
  );
}

/** Estado `loading`: spinner + skeleton (RN-4-05). */
function EsqueletoCarga() {
  return (
    <section className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <p className="mb-4 flex items-center gap-2 text-sm font-medium text-slate-600">
        <Loader2 className="h-4 w-4 animate-spin text-emerald-600" aria-hidden />
        Auditando documento…
      </p>
      <div className="space-y-3" aria-hidden>
        <div className="h-8 w-1/3 animate-pulse rounded bg-slate-200" />
        <div className="h-16 w-full animate-pulse rounded bg-slate-200" />
        <div className="h-40 w-full animate-pulse rounded bg-slate-200" />
      </div>
    </section>
  );
}

/** Estado `idle`: instrucciones + flecha a los ejemplos (RN-4-05, CU-01 Given). */
function EstadoInicial() {
  return (
    <section className="flex h-full min-h-64 flex-col items-center justify-center gap-3 rounded-xl border-2 border-dashed border-slate-300 bg-white/60 p-8 text-center">
      <MousePointerClick className="h-10 w-10 text-slate-400" aria-hidden />
      <h2 className="text-lg font-semibold text-slate-800">Pantalla lista para auditar</h2>
      <p className="max-w-md text-sm text-slate-500">
        Elegí uno de los <strong>3 ejemplos</strong> de la barra superior o{" "}
        <strong>subí un PDF</strong> (máximo 5 MB). El documento se ve a la izquierda y el dictamen
        del auditor aparece en este panel.
      </p>
      <p className="flex items-center gap-1 text-xs text-slate-400">
        <FileText className="h-3 w-3" aria-hidden />
        La IA solo extrae datos; el semáforo lo decide un motor de reglas determinista (R0–R5).
      </p>
    </section>
  );
}
