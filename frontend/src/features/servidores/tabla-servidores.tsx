"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { Database, KeyRound, PlugZap } from "lucide-react";
import { useCallback, useMemo, useState } from "react";
import { toast } from "sonner";
import { Chip } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Ordenable, TablaDatos } from "@/components/tabla-datos";
import { Button } from "@/components/ui/button";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import type { PruebaConexion, Servidor } from "@/lib/tipos";

/** Los 3 servidores de SQL Server con su test de conexión. Las credenciales viven solo en el .env de la API. */
export function TablaServidores() {
  const consulta = useConsulta("servidores", api.servidores);
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

  const columnas = useMemo<ColumnDef<Servidor, unknown>[]>(() => [
    {
      id: "nombre", accessorFn: (s) => `${s.nombre} ${s.servidor}`,
      header: ({ column }) => <Ordenable column={column}>Servidor</Ordenable>,
      cell: ({ row: { original: s } }) => (
        <span className="flex min-w-0 flex-col">
          <span className="flex items-center gap-2 font-medium"><Database className="size-4 text-muted-foreground" />{s.nombre}</span>
          <span className="font-mono text-xs text-muted-foreground">{s.servidor}</span>
        </span>
      ),
    },
    {
      id: "autenticacion", accessorFn: (s) => s.autenticacion,
      header: ({ column }) => <Ordenable column={column}>Autenticación</Ordenable>,
      cell: ({ row: { original: s } }) => (
        <span className="flex items-center gap-1.5">
          {s.autenticacion}
          {s.autenticacion === "SQL" && <Chip tono={s.credenciales_en_env ? "exito" : "aviso"}><KeyRound className="size-3" />{s.credenciales_en_env ? "en .env" : "faltan en .env"}</Chip>}
        </span>
      ),
    },
    {
      id: "bases", accessorFn: (s) => s.bases.join(" "), header: "Bases", enableSorting: false,
      cell: ({ row: { original: s } }) => (
        <span className="line-clamp-2 max-w-md text-xs text-muted-foreground" title={s.bases.join(", ")}>
          {s.bases.slice(0, 8).join(", ")}{s.bases.length > 8 && ` y ${s.bases.length - 8} más`}
        </span>
      ),
    },
    {
      id: "estado", enableSorting: false, enableGlobalFilter: false, header: "Última prueba",
      cell: ({ row: { original: s } }) => {
        const r = resultados[s.nombre];
        if (!r) return <Chip>Sin probar</Chip>;
        return (
          <span className="flex flex-col gap-1">
            <Chip tono={r.ok ? "exito" : "peligro"}>{r.ok ? `OK · ${r.milisegundos} ms` : "Falla"}</Chip>
            {!r.ok && <span className="max-w-xs font-mono text-xs break-all text-[var(--mis-danger)]">{r.detalle}</span>}
          </span>
        );
      },
    },
    {
      id: "acciones", enableHiding: false, enableSorting: false, header: () => <span className="sr-only">Acciones</span>,
      cell: ({ row: { original: s } }) => (
        <div className="flex justify-end">
          <Button variant="outline" size="sm" onClick={() => probar(s)} disabled={probando.has(s.nombre)}>
            <PlugZap className={probando.has(s.nombre) ? "animate-pulse" : ""} /> {probando.has(s.nombre) ? "Probando…" : "Test de conexión"}
          </Button>
        </div>
      ),
    },
  ], [resultados, probando, probar]);

  return (
    <Pagina>
      <Marco icono={<Database />} titulo="Bases de datos" descripcion="Las 3 conexiones de SQL Server. Las credenciales viven solo en el .env de la API; aquí no se muestran ni se editan."
        acciones={<Button size="sm" disabled={probando.size > 0 || !consulta.datos} onClick={() => consulta.datos?.forEach(probar)}><PlugZap /> Probar todas</Button>}>
        <TablaDatos columnas={columnas} datos={consulta.datos} cargando={consulta.cargando} error={consulta.error} onRecargar={consulta.recargar}
          buscar="Buscar servidor o base…" porPagina={7}
          nombres={{ nombre: "Servidor", autenticacion: "Autenticación", bases: "Bases", estado: "Última prueba" }}
          vacio={{ icono: Database, titulo: "Sin servidores" }} />
      </Marco>
    </Pagina>
  );
}
