/**
 * Hook de auditoría (MOD-04 T-05): máquina de estados
 * `idle | loading | resultado | error` sobre React state (sin store global,
 * RN-4-02). Expone `auditar(ejemploId | File)` y `verDetalle(id)` (CU-04).
 *
 * Guarda `pdfUrl` para el visor: URL de la API para ejemplos y blob URL para
 * archivos subidos (RN-4-04); los blob URLs se revocan al reemplazar/desmontar.
 */
import { useCallback, useEffect, useRef, useState } from "react";
import type { ResultadoAuditoria } from "../domain/types";
import {
  ErrorApi,
  aErrorApi,
  auditarArchivo,
  auditarEjemplo,
  obtenerAuditoria,
  obtenerPdfEjemplo,
} from "../infrastructure/apiClient";

export type EstadoAuditoria = "idle" | "loading" | "resultado" | "error";

interface UseAuditoria {
  estado: EstadoAuditoria;
  /** Última auditoría completa; se conserva visible si luego hay error (CU-05). */
  resultado: ResultadoAuditoria | null;
  /** URL para el visor: ejemplo vía API o blob del archivo subido. */
  pdfUrl: string | null;
  error: ErrorApi | null;
  /** Audita un ejemplo (id) o un archivo subido; `null` = terminó en error. */
  auditar: (destino: string | File) => Promise<ResultadoAuditoria | null>;
  /** Re-carga el detalle completo desde el historial (el PDF no se persiste). */
  verDetalle: (id: string) => Promise<ResultadoAuditoria | null>;
}

export function useAuditoria(): UseAuditoria {
  const [estado, setEstado] = useState<EstadoAuditoria>("idle");
  const [resultado, setResultado] = useState<ResultadoAuditoria | null>(null);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [error, setError] = useState<ErrorApi | null>(null);
  const blobUrlRef = useRef<string | null>(null);

  const liberarBlob = useCallback(() => {
    if (blobUrlRef.current) {
      URL.revokeObjectURL(blobUrlRef.current);
      blobUrlRef.current = null;
    }
  }, []);

  // Revoca el último blob URL al desmontar (limpieza, T-15).
  useEffect(() => liberarBlob, [liberarBlob]);

  const auditar = useCallback(
    async (destino: string | File): Promise<ResultadoAuditoria | null> => {
      setEstado("loading");
      setError(null);
      // El PDF aparece en el visor de inmediato, mientras se audita (CU-01).
      liberarBlob();
      if (typeof destino === "string") {
        setPdfUrl(obtenerPdfEjemplo(destino));
      } else {
        const url = URL.createObjectURL(destino);
        blobUrlRef.current = url;
        setPdfUrl(url);
      }
      try {
        const registro =
          typeof destino === "string"
            ? await auditarEjemplo(destino)
            : await auditarArchivo(destino);
        setResultado(registro);
        setEstado("resultado");
        return registro;
      } catch (causa: unknown) {
        setError(aErrorApi(causa));
        setEstado("error");
        return null;
      }
    },
    [liberarBlob],
  );

  const verDetalle = useCallback(
    async (id: string): Promise<ResultadoAuditoria | null> => {
      setEstado("loading");
      setError(null);
      liberarBlob();
      setPdfUrl(null); // los archivos subidos no se persisten: solo datos (CU-04)
      try {
        const detalle = await obtenerAuditoria(id);
        setResultado(detalle);
        setEstado("resultado");
        return detalle;
      } catch (causa: unknown) {
        setError(aErrorApi(causa));
        setEstado("error");
        return null;
      }
    },
    [liberarBlob],
  );

  return { estado, resultado, pdfUrl, error, auditar, verDetalle };
}
