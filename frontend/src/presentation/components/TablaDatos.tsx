/**
 * Tabla de datos extraídos (MOD-04 T-11): cabecera del comprobante + tabla de
 * ítems + fila de total resaltada, con montos formateados `es-AR`. Estado
 * vacío si `datos_extraidos` es `null` (extracción fallida). Solo renderiza
 * lo que devuelve la API (RN-4-01).
 */
import type { FacturaExtraida } from "../../domain/types";
import { formatoArs, formatoCantidad, formatoFecha } from "../formato";

interface Props {
  datos: FacturaExtraida | null;
}

export function TablaDatos({ datos }: Props) {
  if (!datos) {
    return (
      <section className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <h2 className="text-sm font-semibold text-slate-700">Datos extraídos</h2>
        <p className="mt-2 text-sm text-slate-500">
          Sin datos extraídos: la extracción con IA falló o el comprobante fue rechazado por
          admisión.
        </p>
      </section>
    );
  }
  return (
    <section className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-sm">
      <h2 className="border-b border-slate-200 px-4 py-2 text-sm font-semibold text-slate-700">
        Datos extraídos
      </h2>
      <dl className="grid grid-cols-2 gap-x-4 gap-y-3 px-4 py-3 text-sm sm:grid-cols-4">
        <Campo etiqueta="Tipo" valor={datos.tipo_comprobante} />
        <Campo etiqueta="Número" valor={datos.numero_comprobante ?? "—"} mono />
        <Campo etiqueta="CUIT emisor" valor={datos.cuit_emisor} mono />
        <Campo etiqueta="Razón social" valor={datos.razon_social} />
        <Campo etiqueta="Fecha de emisión" valor={formatoFecha(datos.fecha_emision)} />
        <Campo etiqueta="Orden de compra" valor={datos.numero_orden_compra ?? "—"} mono />
        <Campo etiqueta="Impuestos" valor={formatoArs(datos.impuestos)} />
        <Campo etiqueta="Total" valor={formatoArs(datos.monto_total)} resaltado />
      </dl>
      <div className="overflow-x-auto border-t border-slate-200">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
            <tr>
              <th scope="col" className="px-4 py-2 font-medium">
                Descripción
              </th>
              <th scope="col" className="px-4 py-2 text-right font-medium">
                Cantidad
              </th>
              <th scope="col" className="px-4 py-2 text-right font-medium">
                Precio unitario
              </th>
              <th scope="col" className="px-4 py-2 text-right font-medium">
                Subtotal
              </th>
            </tr>
          </thead>
          <tbody>
            {datos.items.map((item, indice) => (
              <tr key={indice} className="border-t border-slate-100">
                <td className="px-4 py-2 text-slate-800">{item.descripcion}</td>
                <td className="px-4 py-2 text-right text-slate-700">
                  {formatoCantidad(item.cantidad)}
                </td>
                <td className="px-4 py-2 text-right text-slate-700">
                  {formatoArs(item.precio_unitario)}
                </td>
                <td className="px-4 py-2 text-right text-slate-700">{formatoArs(item.subtotal)}</td>
              </tr>
            ))}
          </tbody>
          <tfoot>
            <tr className="border-t-2 border-slate-300 bg-slate-50 font-semibold text-slate-900">
              <td className="px-4 py-2" colSpan={3}>
                Total del comprobante
              </td>
              <td className="px-4 py-2 text-right">{formatoArs(datos.monto_total)}</td>
            </tr>
          </tfoot>
        </table>
      </div>
    </section>
  );
}

function Campo({
  etiqueta,
  valor,
  mono = false,
  resaltado = false,
}: {
  etiqueta: string;
  valor: string;
  mono?: boolean;
  resaltado?: boolean;
}) {
  return (
    <div className="min-w-0">
      <dt className="text-xs uppercase tracking-wide text-slate-400">{etiqueta}</dt>
      <dd
        className={`truncate ${mono ? "font-mono" : ""} ${
          resaltado ? "text-base font-bold text-slate-900" : "text-slate-800"
        }`}
        title={valor}
      >
        {valor}
      </dd>
    </div>
  );
}
