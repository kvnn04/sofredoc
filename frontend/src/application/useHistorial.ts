/**
 * Hook del historial (MOD-04 T-06): listado paginado de `GET /historial`
 * con `refrescar()` para invocarlo tras cada auditoría exitosa (CU-04).
 */
import { useCallback, useEffect, useState } from "react";
import type { ResumenAuditoria } from "../domain/types";
import { aErrorApi, listarHistorial } from "../infrastructure/apiClient";
import type { ErrorApi } from "../infrastructure/apiClient";

/** Tamaño de página default del contrato (`limit=20`). */
const LIMIT = 20;

interface UseHistorial {
  historial: ResumenAuditoria[];
  cargando: boolean;
  error: ErrorApi | null;
  offset: number;
  hayMas: boolean;
  /** Se invoca tras cada auditoría exitosa (T-06). */
  refrescar: () => Promise<void>;
  avanzar: () => void;
  retroceder: () => void;
}

export function useHistorial(): UseHistorial {
  const [historial, setHistorial] = useState<ResumenAuditoria[]>([]);
  const [cargando, setCargando] = useState(true); // la carga empieza al montar
  const [error, setError] = useState<ErrorApi | null>(null);
  const [offset, setOffset] = useState(0);
  const [hayMas, setHayMas] = useState(false);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    let vivo = true;
    listarHistorial(LIMIT, offset)
      .then((filas) => {
        if (!vivo) return;
        setHistorial(filas);
        setHayMas(filas.length === LIMIT);
        setError(null);
      })
      .catch((causa: unknown) => {
        if (vivo) setError(aErrorApi(causa));
      })
      .finally(() => {
        if (vivo) setCargando(false);
      });
    return () => {
      vivo = false;
    };
  }, [offset, intento]);

  const refrescar = useCallback(async () => {
    setCargando(true);
    setError(null);
    setIntento((n) => n + 1);
  }, []);

  const avanzar = useCallback(() => {
    setCargando(true);
    setError(null);
    setOffset((actual) => actual + LIMIT);
  }, []);

  const retroceder = useCallback(() => {
    setCargando(true);
    setError(null);
    setOffset((actual) => Math.max(0, actual - LIMIT));
  }, []);

  return { historial, cargando, error, offset, hayMas, refrescar, avanzar, retroceder };
}
