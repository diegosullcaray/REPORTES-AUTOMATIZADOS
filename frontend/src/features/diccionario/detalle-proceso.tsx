"use client";

import type { ColumnDef } from "@tanstack/react-table";
import { ArrowLeft, Play } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useMemo, useState } from "react";
import { toast } from "sonner";
import { Chip, ErrorEnLinea, EsqueletoFilas, EstadoVacio } from "@/components/estados";
import { Confirmar } from "@/components/confirmar";
import { Hace } from "@/components/hace";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Ordenable, TablaDatos } from "@/components/tabla-datos";
import { Tarjeta } from "@/components/tarjeta";
import { Terminal } from "@/components/terminal";
import { Button, buttonVariants } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Codigo } from "@/features/reportes/detalle/panel-script";
import { useConsulta, type Consulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { tamano } from "@/lib/formato";
import type { DicArchivoProceso, DicEjecucion, DicProcesoDetalle } from "@/lib/tipos";
import { ESTADO, LogEjecucion, TablaEjecuciones } from "./ejecuciones";
import { ICONO_PROCESO } from "./procesos";

/** Verbo del botón y texto de la confirmación de los procesos que corren dentro de la API (los de npm usan «Ejecutar» y el comando). */
const VERBO: Record<string, string> = { bases: "Validar", construir: "Generar" };
const AVISO_CONFIRMAR: Record<string, string> = {
  bases: "Prueba la conexión a cada servidor SQL y que cada base que usan los reportes esté en línea. No escribe nada.",
  construir: "Lee el catálogo de reportes (mod_rep.rep.RREGREP01) y los metadatos de cada base, solo lectura, y guarda el diccionario en esta app. Puede tardar un minuto.",
};

const PESTANAS = ["general", "ejecuciones", "script", "archivos"] as const;
type Pestana = (typeof PESTANAS)[number];

/** Lenguaje con que se resalta cada pieza del script: la consulta SQL, el script de package.json (shell) o el archivo que ejecuta. */
const lenguaje = (ruta: string) => (ruta.startsWith("SQL") ? "sql" : ruta.startsWith("package.json") ? "bash" : ruta.includes(".py") ? "python" : "javascript");

function General({ p, ejecuciones, onLog }: { p: DicProcesoDetalle; ejecuciones: Consulta<DicEjecucion[]>; onLog: (id: string) => void }) {
  const [pedido, setPedido] = useState(false);
  const ultima = ejecuciones.datos?.[0];
  const { datos: detalle } = useConsulta(ultima ? `dic/ejecucion/${ultima.id}` : null, () => api.dic.ejecucion(ultima!.id), (d) => d.estado === "ejecutando", 1500);

  async function lanzar() {
    try {
      await api.dic.ejecutar(p.id);
      ejecuciones.recargar();
    } catch (e) {
      toast.error("No se pudo lanzar", { description: (e as Error).message });
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <Tarjeta titulo="Qué hace" descripcion={p.descripcion}
        acciones={<Button size="sm" disabled={ultima?.estado === "ejecutando"} onClick={() => setPedido(true)}><Play /> {VERBO[p.id] ?? "Ejecutar"}</Button>}>
        <dl className="grid gap-x-6 gap-y-2 text-sm sm:grid-cols-[auto_1fr]">
          <dt className="text-muted-foreground">{p.id === "bases" || p.id === "construir" ? "Consulta" : "Comando"}</dt><dd className="font-mono text-[13px]">{p.comando}</dd>
          <dt className="text-muted-foreground">Escribe en</dt><dd>{p.escribe}</dd>
          <dt className="text-muted-foreground">Deja archivos</dt><dd>{p.genera ? `Sí: ${p.archivos.length} para ver en la pestaña Archivos` : "No: su resultado está en el log de cada ejecución"}</dd>
        </dl>
      </Tarjeta>
      <Tarjeta titulo="Última ejecución" descripcion={ultima ? <>{ESTADO[ultima.estado].texto} · <Hace iso={ultima.inicio} /></> : "Todavía no se ejecutó desde la web."}
        acciones={ultima && <Button variant="outline" size="sm" onClick={() => onLog(ultima.id)}>Abrir el log</Button>}>
        {ultima && <Terminal titulo={p.id} texto={detalle?.log ?? ""} estado={<Chip tono={ESTADO[ultima.estado].tono}>{ESTADO[ultima.estado].texto}</Chip>} />}
      </Tarjeta>
      <Confirmar abierto={pedido} onAbierto={setPedido} titulo={`¿Ejecutar «${p.nombre}»?`} accion={VERBO[p.id] ?? "Ejecutar"}
        descripcion={AVISO_CONFIRMAR[p.id] ?? <>Corre <span className="font-mono">{p.comando}</span> en el repo DICCIONARIO. Escribe en: {p.escribe}.</>}
        onConfirmar={() => { setPedido(false); void lanzar(); }} />
    </div>
  );
}

function Script({ p }: { p: DicProcesoDetalle }) {
  return (
    <div className="flex flex-col gap-4">
      {p.scripts.map((s) => (
        <div key={s.ruta} className="overflow-hidden rounded-lg border" style={{ background: "var(--terminal-bg)" }}>
          <div className="border-b border-white/10 px-3 py-1.5 font-mono text-xs" style={{ color: "var(--terminal-tenue)" }}>{s.ruta}</div>
          <div className="max-h-[60vh] overflow-auto"><Codigo codigo={s.codigo} lang={lenguaje(s.ruta)} /></div>
        </div>
      ))}
    </div>
  );
}

function Archivos({ p }: { p: DicProcesoDetalle }) {
  const [abierto, setAbierto] = useState<string | null>(null);
  const vista = useConsulta(abierto && `dic/archivo/${p.id}/${abierto}`, () => api.dic.archivoProceso(p.id, abierto!));
  const columnas = useMemo<ColumnDef<DicArchivoProceso, unknown>[]>(() => [
    { accessorKey: "ruta", header: ({ column }) => <Ordenable column={column}>Archivo</Ordenable>, cell: ({ row: { original: a } }) => <span className="font-mono text-[13px]">{a.ruta}</span> },
    { accessorKey: "tamano", header: ({ column }) => <Ordenable column={column}>Tamaño</Ordenable>, cell: ({ row: { original: a } }) => <span className="tabular-nums">{tamano(a.tamano)}</span> },
    { accessorKey: "modificado", header: ({ column }) => <Ordenable column={column}>Generado</Ordenable>, cell: ({ row: { original: a } }) => <Hace iso={a.modificado} /> },
    { id: "ver", header: "", enableSorting: false, cell: ({ row: { original: a } }) => (a.tipo === "texto" ? <Button variant="ghost" size="sm" onClick={() => setAbierto(a.ruta)}>Ver</Button> : null) },
  ], []);
  if (!p.genera) return <EstadoVacio titulo="Este proceso no deja archivos" descripcion="Su resultado está en el log de cada ejecución (pestaña Ejecuciones)." />;
  return (
    <>
      <TablaDatos columnas={columnas} datos={p.archivos} cargando={false} error={null} onRecargar={() => {}} buscar="Buscar archivo…"
        vacio={{ titulo: "Sin archivos", descripcion: "Ejecuta el proceso para generarlos." }} ordenInicial={[{ id: "ruta", desc: false }]} nombres={{ ruta: "Archivo", tamano: "Tamaño", modificado: "Generado" }} />
      <Dialog open={!!abierto} onOpenChange={(a) => !a && setAbierto(null)}>
        <DialogContent className="flex max-h-[90vh] flex-col sm:max-w-4xl">
          <DialogHeader><DialogTitle className="font-mono text-base">{abierto}</DialogTitle><DialogDescription>Solo lectura: se regenera con el proceso.{vista.datos?.recortado ? " Se muestra solo el comienzo del archivo." : ""}</DialogDescription></DialogHeader>
          <div className="min-h-0 overflow-auto">
            {vista.error ? <ErrorEnLinea titulo="No se pudo abrir el archivo" detalle={vista.error} /> : !vista.datos ? <EsqueletoFilas filas={6} /> : <Terminal titulo={vista.datos.ruta} texto={vista.datos.texto} />}
          </div>
        </DialogContent>
      </Dialog>
    </>
  );
}

/** Un proceso al detalle (como el de un reporte): general, ejecuciones, script y lo que genera. Pestañas en la URL. */
export function DetalleProceso({ id }: { id: string }) {
  const { datos: p, error, recargar } = useConsulta(`dic/proceso/${id}`, () => api.dic.proceso(id));
  const ejecuciones = useConsulta(`dic/ejecuciones/${id}`, () => api.dic.ejecuciones(id), (d) => d.some((x) => x.estado === "ejecutando"), 2000);
  const [log, setLog] = useState<string | null>(null);
  const router = useRouter();
  const ruta = usePathname();
  const pedida = useSearchParams().get("tab") as Pestana | null;
  const tab: Pestana = pedida && PESTANAS.includes(pedida) ? pedida : "general";
  const irA = (t: Pestana) => router.replace(t === "general" ? ruta : `${ruta}?tab=${t}`, { scroll: false });
  const Icono = ICONO_PROCESO[id] ?? Play;
  return (
    <Pagina>
      <Marco icono={<Icono />} titulo={p?.nombre ?? id} descripcion={p?.descripcion}
        acciones={<Link href="/diccionario/procesos" className={buttonVariants({ variant: "ghost", size: "sm" })}><ArrowLeft /> Procesos</Link>}>
        {error ? <ErrorEnLinea titulo="No se pudo cargar el proceso" detalle={error} onReintentar={recargar} /> : !p ? <EsqueletoFilas filas={4} /> : (
          <Tabs value={tab} onValueChange={(v) => irA(v as Pestana)}>
            <TabsList>
              <TabsTrigger value="general">General</TabsTrigger>
              <TabsTrigger value="ejecuciones">Ejecuciones{ejecuciones.datos ? ` (${ejecuciones.datos.length})` : ""}</TabsTrigger>
              <TabsTrigger value="script">Script</TabsTrigger>
              <TabsTrigger value="archivos">Archivos{p.genera ? ` (${p.archivos.length})` : ""}</TabsTrigger>
            </TabsList>
            <TabsContent value="general" className="pt-3"><General p={p} ejecuciones={ejecuciones} onLog={setLog} /></TabsContent>
            <TabsContent value="ejecuciones" className="pt-3"><TablaEjecuciones consulta={ejecuciones} onLog={setLog} /></TabsContent>
            <TabsContent value="script" className="pt-3"><Script p={p} /></TabsContent>
            <TabsContent value="archivos" className="pt-3"><Archivos p={p} /></TabsContent>
          </Tabs>
        )}
      </Marco>
      <LogEjecucion id={log} onCerrar={() => setLog(null)} />
    </Pagina>
  );
}
