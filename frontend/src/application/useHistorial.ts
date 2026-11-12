/**
 * Hook del historial (MOD-04 T-06): listado paginado de `GET /historial`
 * con `refrescar()` para invocarlo tras cada auditoría exitosa (CU-04).
 */
import { useCallback, useEffect, useState } from "react";
import type { ResumenAuditoria } from "../domain/types";
import { ErrorApi, aErrorApi, listarHistorial } from "../infrastructure/apiClient";

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
  const [cargando, setCargando] = useState(true);
  const [error, setError] = useState<ErrorApi | null>(null);
  const [offset, setOffset] = useState(0);
  const [hayMas, setHayMas] = useState(false);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    let vivo = true;
    setCargando(true);
    setError(null);
    listarHistorial(LIMIT, offset)
      .then((filas) => {
        if (!vivo) return;
        setHistorial(filas);
        setHayMas(filas.length === LIMIT);
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
    setIntento((n) => n + 1);
  }, []);

  return {
    historial,
    cargando,
    error,
    offset,
    hayMas,
    refrescar,
    avanzar: () => setOffset((actual) => actual + LIMIT),
    retroceder: () => setOffset((actual) => Math.max(0, actual - LIMIT)),
  };
}
