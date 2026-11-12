/**
 * Hook del catálogo de ejemplos (MOD-04 T-04): carga `GET /ejemplos` al montar.
 */
import { useCallback, useEffect, useState } from "react";
import type { Ejemplo } from "../domain/types";
import { aErrorApi, listarEjemplos } from "../infrastructure/apiClient";
import type { ErrorApi } from "../infrastructure/apiClient";

interface UseEjemplos {
  ejemplos: Ejemplo[];
  cargando: boolean;
  error: ErrorApi | null;
  /** Reintenta la carga (tras un ERROR_RED, por ejemplo). */
  recargar: () => void;
}

export function useEjemplos(): UseEjemplos {
  const [ejemplos, setEjemplos] = useState<Ejemplo[]>([]);
  const [cargando, setCargando] = useState(true); // la carga empieza al montar
  const [error, setError] = useState<ErrorApi | null>(null);
  const [intento, setIntento] = useState(0);

  useEffect(() => {
    let vivo = true;
    listarEjemplos()
      .then((lista) => {
        if (!vivo) return;
        setEjemplos(lista);
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
  }, [intento]);

  const recargar = useCallback(() => {
    setCargando(true);
    setError(null);
    setIntento((n) => n + 1);
  }, []);

  return { ejemplos, cargando, error, recargar };
}
