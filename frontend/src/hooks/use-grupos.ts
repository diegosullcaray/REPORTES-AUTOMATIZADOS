"use client";

import { api } from "@/lib/api";
import type { GrupoReportes } from "@/lib/tipos";
import { useConsulta, type Consulta } from "./use-consulta";

/** Grupos de reportes (los del legado y los creados desde la web) con una búsqueda de nombre por id. */
export function useGrupos(activo = true): Consulta<GrupoReportes[]> & { nombre: (id: string) => string } {
  const c = useConsulta(activo ? "grupos" : null, api.grupos);
  return { ...c, nombre: (id) => c.datos?.find((g) => g.id === id)?.nombre ?? id };
}
