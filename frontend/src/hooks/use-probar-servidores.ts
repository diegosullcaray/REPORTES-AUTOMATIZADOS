"use client";

import { useCallback, useState } from "react";
import { toast } from "sonner";
import { api } from "@/lib/api";
import type { PruebaConexion, Servidor } from "@/lib/tipos";

/** Test de conexión a un servidor SQL (SELECT 1): quién se está probando y el último resultado de cada uno. */
export function useProbarServidores() {
  const [probando, setProbando] = useState<ReadonlySet<string>>(new Set());
  const [resultados, setResultados] = useState<Record<string, PruebaConexion>>({});

  const probar = useCallback(async (s: Servidor) => {
    setProbando((p) => new Set(p).add(s.nombre));
    try {
      const r = await api.probarServidor(s.nombre);
      setResultados((x) => ({ ...x, [s.nombre]: r }));
      if (r.ok) toast.success(`${s.nombre}: conexión correcta`, { description: `${s.servidor} · ${r.milisegundos} ms` });
      else toast.error(`${s.nombre}: sin conexión`, { description: r.detalle });
    } catch (e) {
      toast.error("No se pudo probar la conexión", { description: (e as Error).message });
    } finally {
      setProbando((p) => { const n = new Set(p); n.delete(s.nombre); return n; });
    }
  }, []);

  return { probando, resultados, probar };
}
