"use client";

import { ArrowLeft, Database, FileSpreadsheet, Mail, Server, UserRound } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { EsqueletoFilas, ErrorEnLinea, Punto } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Pagina } from "@/components/pagina";
import { Tarjeta } from "@/components/tarjeta";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { ListaEjecuciones } from "@/features/ejecuciones/lista-ejecuciones";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, TIPO, enCurso, titulo } from "@/lib/formato";
import { CampoCorte } from "./campo-corte";
import { PanelArchivos } from "./panel-archivos";
import { PanelCorreo } from "./panel-correo";
import { PanelGeneral } from "./panel-general";

const PESTANAS = ["general", "ejecuciones", "archivos", "correo"] as const;
type Pestana = (typeof PESTANAS)[number];

/** Reporte con la estructura de un servicio en Dokploy: encabezado (ícono + estado, nombre, insignias) y pestañas en la URL. */
export function DetalleReporte({ nombre }: { nombre: string }) {
  const { datos: r, error, cargando, recargar } = useConsulta(`reporte/${nombre}`, () => api.reporte(nombre));
  const { datos: ultimas } = useConsulta(`ultima/${nombre}`, () => api.ejecuciones(nombre, 1), () => true, 5000);
  const params = useSearchParams();
  const router = useRouter();
  const ruta = usePathname();
  const pedida = params.get("tab") as Pestana | null;
  const pestana: Pestana = pedida && PESTANAS.includes(pedida) && (pedida !== "correo" || r?.envia_correo) ? pedida : "general";
  const irA = (p: Pestana) => router.replace(p === "general" ? ruta : `${ruta}?tab=${p}`, { scroll: false });

  const [elegido, setCorte] = useState<string | null>(null); // null = la fecha por defecto del reporte
  const corte = elegido ?? r?.corte.fecha ?? "";
  const ultima = ultimas?.[0];
  const estado = ultima ? ESTADO_EJECUCION[ultima.estado] : null;

  return (
    <Pagina>
      <section className="flex flex-1 flex-col rounded-xl bg-sidebar p-2 sm:p-2.5">
        <div className="flex flex-1 flex-col rounded-xl border bg-background shadow-sm">
          <header className="flex flex-col gap-4 p-4 sm:flex-row sm:items-start sm:justify-between sm:p-6">
            <div className="flex min-w-0 items-start gap-4">
              <span className="relative flex size-12 shrink-0 items-center justify-center rounded-xl border bg-muted">
                <FileSpreadsheet className="size-6 text-muted-foreground" />
                <span className="absolute -top-1 -right-1">
                  <Punto tono={estado?.tono ?? "neutro"} etiqueta={estado?.texto ?? "Sin ejecuciones"} latido={!!ultima && enCurso(ultima.estado)} />
                </span>
              </span>
              <div className="flex min-w-0 flex-col gap-1">
                <h1 className="flex flex-wrap items-center gap-2 text-xl font-semibold tracking-tight">
                  {titulo(nombre)}
                  {r?.escribe_en_bd && <Database aria-label="escribe en BD" className="size-4 text-[var(--mis-warning)]" />}
                  {r?.envia_correo && <Mail aria-label="envía correo" className="size-4 text-muted-foreground" />}
                </h1>
                {r && <p className="text-sm text-muted-foreground">{r.descripcion}</p>}
              </div>
            </div>
            <div className="flex flex-col gap-2 sm:items-end">
              {r && (
                <div className="flex flex-wrap gap-2">
                  <Badge>{TIPO[r.frecuencia]}</Badge>
                  <Badge variant="outline" className="gap-1"><Server className="size-3" />{r.servidores.join(", ")}</Badge>
                  {r.grupo !== "diarias" && <Badge variant="outline" className="gap-1"><UserRound className="size-3" />{r.grupo === "piero" ? "Piero" : "Erick"} · {r.orden}</Badge>}
                </div>
              )}
              <span className="text-xs text-muted-foreground">
                {ultima && estado ? <>Última ejecución: {estado.texto.toLowerCase()} · <Hace iso={ultima.inicio} /></> : "Sin ejecuciones desde la web"}
              </span>
              <Link href="/reportes" className={`${buttonVariants({ variant: "ghost", size: "sm" })} sm:hidden`}><ArrowLeft /> Reportes</Link>
            </div>
          </header>

          <div className="flex-1 border-t p-4 sm:p-6">
            {error ? (
              <ErrorEnLinea titulo="No se pudo cargar el reporte" detalle={error} onReintentar={recargar} />
            ) : cargando && !r ? (
              <EsqueletoFilas filas={5} />
            ) : r && (
              <div className="flex flex-col gap-4">
              <CampoCorte reporte={r} valor={corte} onCambio={setCorte} />
              <Tabs value={pestana} onValueChange={(v) => irA(v as Pestana)}>
                <TabsList className="w-full justify-start overflow-x-auto no-scrollbar sm:w-fit">
                  <TabsTrigger value="general">General</TabsTrigger>
                  <TabsTrigger value="ejecuciones">Ejecuciones</TabsTrigger>
                  <TabsTrigger value="archivos">Archivos</TabsTrigger>
                  {r.envia_correo && <TabsTrigger value="correo">Correo</TabsTrigger>}
                </TabsList>
                <TabsContent value="general" className="pt-3">
                  <PanelGeneral reporte={r} corte={corte} />
                </TabsContent>
                <TabsContent value="ejecuciones" className="pt-3"><ListaEjecuciones reporte={r.nombre} /></TabsContent>
                <TabsContent value="archivos" className="pt-3">
                  <Tarjeta titulo="Archivos" descripcion={`Carpeta de salida: data/outputs/${r.carpeta}`}>
                    <PanelArchivos reporte={r.nombre} />
                  </Tarjeta>
                </TabsContent>
                {r.envia_correo && (
                  <TabsContent value="correo" className="pt-3">
                    <Tarjeta titulo="Correo" descripcion="Prueba → conforme → envío a toda la lista.">
                      <PanelCorreo reporte={r} corte={corte} />
                    </Tarjeta>
                  </TabsContent>
                )}
              </Tabs>
              </div>
            )}
          </div>
        </div>
      </section>
    </Pagina>
  );
}
