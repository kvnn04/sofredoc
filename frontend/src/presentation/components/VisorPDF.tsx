/**
 * Visor de PDF (MOD-04 T-09): columna izquierda (~40%) con un `iframe` que
 * apunta a la URL de la API (ejemplos) o al blob URL del archivo subido
 * (RN-4-04). Incluye fallback de texto si el navegador bloquea el embed.
 */
import { FileText } from "lucide-react";

interface Props {
  pdfUrl: string | null;
  nombreArchivo: string | null;
}

export function VisorPDF({ pdfUrl, nombreArchivo }: Props) {
  return (
    <section className="flex h-full min-h-0 flex-col rounded-xl border border-slate-200 bg-white shadow-sm">
      <header className="flex items-center justify-between gap-2 border-b border-slate-200 px-4 py-2">
        <h2 className="flex items-center gap-2 text-sm font-semibold text-slate-700">
          <FileText className="h-4 w-4 text-slate-500" aria-hidden />
          Documento
          {nombreArchivo && (
            <span
              className="max-w-[14rem] truncate text-xs font-normal text-slate-500"
              title={nombreArchivo}
            >
              · {nombreArchivo}
            </span>
          )}
        </h2>
        {pdfUrl && (
          <a
            href={pdfUrl}
            target="_blank"
            rel="noreferrer"
            className="text-xs font-medium text-sky-700 hover:underline"
          >
            Abrir en otra pestaña
          </a>
        )}
      </header>
      <div className="min-h-0 flex-1">
        {pdfUrl ? (
          <iframe
            src={pdfUrl}
            title={`Visor de ${nombreArchivo ?? "PDF"}`}
            className="h-full w-full rounded-b-xl"
          >
            <p className="p-4 text-sm text-slate-600">
              Tu navegador bloqueó el visor embebido.{" "}
              <a href={pdfUrl} target="_blank" rel="noreferrer" className="text-sky-700 underline">
                Abrir el PDF en otra pestaña
              </a>
            </p>
          </iframe>
        ) : (
          <div className="flex h-full flex-col items-center justify-center gap-2 p-6 text-center">
            <FileText className="h-10 w-10 text-slate-300" aria-hidden />
            <p className="text-sm text-slate-500">
              {nombreArchivo
                ? `El archivo "${nombreArchivo}" no tiene PDF asociado (los archivos subidos no se persisten; solo se muestran ejemplos y subidas recientes).`
                : "Sin documento. Elegí un ejemplo o subí un PDF para verlo acá."}
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
