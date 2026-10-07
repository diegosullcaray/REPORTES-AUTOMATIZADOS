"use client";

import { useCallback, useEffect, useRef, useState } from "react";

export interface Consulta<T> {
  datos: T | undefined;
  error: string | null;
  cargando: boolean; // hay una petición en vuelo
  recargar: () => void;
}

/**
 * Estado de una lectura: error · cargando · vacío · contenido (en ese orden lo pinta quien la usa).
 * `clave` null = no consultar. `cadaMs` repite mientras devuelva true para los datos actuales (polling).
 */
export function useConsulta<T>(clave: string | null, leer: () => Promise<T>, cadaMs?: (datos: T) => boolean, intervalo = 2000): Consulta<T> {
  const [datos, setDatos] = useState<T>();
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(clave !== null);
  const [vuelta, setVuelta] = useState(0);
  const leerRef = useRef(leer);
  const repetirRef = useRef(cadaMs);
  useEffect(() => {
    leerRef.current = leer;
    repetirRef.current = cadaMs;
  });

  useEffect(() => {
    if (clave === null) return;
    let vivo = true;
    let temporizador: ReturnType<typeof setTimeout>;
    const correr = async () => {
      setCargando(true);
      try {
        const d = await leerRef.current();
        if (!vivo) return;
        setDatos(d);
        setError(null);
        if (repetirRef.current?.(d)) temporizador = setTimeout(correr, intervalo);
      } catch (e) {
        if (vivo) setError(e instanceof Error ? e.message : String(e));
      } finally {
        if (vivo) setCargando(false);
      }
    };
    correr();
    return () => {
      vivo = false;
      clearTimeout(temporizador);
    };
  }, [clave, vuelta, intervalo]);

  const recargar = useCallback(() => setVuelta((v) => v + 1), []);
  return { datos, error, cargando, recargar };
}
