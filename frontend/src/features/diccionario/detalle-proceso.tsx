"use client";

import { ArrowLeft, Play } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";
import { Chip, ErrorEnLinea, EsqueletoFilas } from "@/components/estados";
import { Confirmar } from "@/components/confirmar";
import { Hace } from "@/components/hace";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Tarjeta } from "@/components/tarjeta";
import { Terminal } from "@/components/terminal";
import { Button, buttonVariants } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Codigo } from "@/features/reportes/detalle/panel-script";
import { useConsulta, type Consulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import type { DicEjecucion, DicProcesoDetalle } from "@/lib/tipos";
import { ESTADO, LogEjecucion, TablaEjecuciones } from "./ejecuciones";
import { ICONO_PROCESO } from "./procesos";

/** Verbo del botón y texto de la confirmación de cada proceso. */
const VERBO: Record<string, string> = { bases: "Validar", construir: "Generar" };
const AVISO_CONFIRMAR: Record<string, string> = {
  bases: "Prueba la conexión a cada servidor SQL y que cada base que usan los reportes esté en línea. No escribe nada.",
  construir: "Lee el catálogo de reportes (mod_rep.rep.RREGREP01) y los metadatos de cada base, solo lectura, y guarda el diccionario en esta app. Puede tardar un minuto.",
};

const PESTANAS = ["general", "ejecuciones", "script"] as const;
type Pestana = (typeof PESTANAS)[number];

/** Lenguaje con que se resalta cada pieza del script: la consulta SQL o el código Python que la usa. */
const lenguaje = (ruta: string) => (ruta.startsWith("SQL") ? "sql" : "python");

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
        acciones={<Button size="sm" disabled={ultima?.estado === "ejecutando"} onClick={() => setPedido(true)}><Play /> {VERBO[p.id]}</Button>}>
        <dl className="grid gap-x-6 gap-y-2 text-sm sm:grid-cols-[auto_1fr]">
          <dt className="text-muted-foreground">Consulta</dt><dd className="font-mono text-[13px]">{p.comando}</dd>
          <dt className="text-muted-foreground">Escribe en</dt><dd>{p.escribe}</dd>
        </dl>
      </Tarjeta>
      <Tarjeta titulo="Última ejecución" descripcion={ultima ? <>{ESTADO[ultima.estado].texto} · <Hace iso={ultima.inicio} /></> : "Todavía no se ejecutó desde la web."}
        acciones={ultima && <Button variant="outline" size="sm" onClick={() => onLog(ultima.id)}>Abrir el log</Button>}>
        {ultima && <Terminal titulo={p.id} texto={detalle?.log ?? ""} estado={<Chip tono={ESTADO[ultima.estado].tono}>{ESTADO[ultima.estado].texto}</Chip>} />}
      </Tarjeta>
      <Confirmar abierto={pedido} onAbierto={setPedido} titulo={`¿Ejecutar «${p.nombre}»?`} accion={VERBO[p.id]}
        descripcion={AVISO_CONFIRMAR[p.id]}
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

/** Un proceso al detalle (como el de un reporte): general, ejecuciones y script. Pestañas en la URL. */
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
            </TabsList>
            <TabsContent value="general" className="pt-3"><General p={p} ejecuciones={ejecuciones} onLog={setLog} /></TabsContent>
            <TabsContent value="ejecuciones" className="pt-3"><TablaEjecuciones consulta={ejecuciones} onLog={setLog} /></TabsContent>
            <TabsContent value="script" className="pt-3"><Script p={p} /></TabsContent>
          </Tabs>
        )}
      </Marco>
      <LogEjecucion id={log} onCerrar={() => setLog(null)} />
    </Pagina>
  );
}
