import { FileText, ShieldCheck } from "lucide-react";

/**
 * Pantalla base del MVP (MOD-00).
 * La pantalla dividida real (visor PDF + resultados) se construye en MOD-04.
 */
export default function App() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-50 text-slate-900">
      <ShieldCheck className="h-12 w-12 text-emerald-600" aria-hidden />
      <h1 className="text-3xl font-bold">SofreDoc Validator</h1>
      <p className="flex items-center gap-2 text-slate-600">
        <FileText className="h-4 w-4" aria-hidden />
        Auditoría de facturas con IA — MVP en construcción
      </p>
    </main>
  );
}
