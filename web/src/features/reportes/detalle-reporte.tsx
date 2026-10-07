"use client";

import { ArrowLeft, Database, FileSpreadsheet, Mail } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { EsqueletoFilas, ErrorEnLinea, Punto } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { TablaEjecuciones } from "@/features/ejecuciones/tabla-ejecuciones";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, TIPO, enCurso, titulo } from "@/lib/formato";
import type { Verificacion } from "@/lib/tipos";
import { PanelArchivos } from "./panel-archivos";
import { PanelCorreo } from "./panel-correo";
import { PanelEjecucion } from "./panel-ejecucion";
import { PanelValidacion } from "./panel-validacion";

const PESTANAS = ["ejecucion", "validacion", "archivos", "correo", "historial"] as const;
type Pestana = (typeof PESTANAS)[number];

/** Reporte (como la vista de un servicio en Dokploy): encabezado con estado de la última ejecución y pestañas en la URL. */
export function DetalleReporte({ nombre }: { nombre: string }) {
  const { datos: r, error, cargando, recargar } = useConsulta(`reporte/${nombre}`, () => api.reporte(nombre));
  const { datos: ultimas } = useConsulta(`ultima/${nombre}`, () => api.ejecuciones(nombre, 1), () => true, 5000);
  const params = useSearchParams();
  const router = useRouter();
  const ruta = usePathname();
  const pedida = params.get("tab") as Pestana | null;
  const pestana: Pestana = pedida && PESTANAS.includes(pedida) && (pedida !== "correo" || r?.envia_correo) ? pedida : "ejecucion";
  const setPestana = (p: Pestana) => router.replace(p === "ejecucion" ? ruta : `${ruta}?tab=${p}`, { scroll: false });

  const [elegido, setCorte] = useState<string | null>(null); // null = la fecha por defecto del reporte
  const [verificacion, setVerificacion] = useState<Verificacion | null>(null);
  const corte = elegido ?? r?.corte.fecha ?? "";
  const ultima = ultimas?.[0];

  const encabezado = (
    <span className="flex items-center gap-2.5">
      {titulo(nombre)}
      {r && <Badge variant="secondary">{TIPO[r.frecuencia]}</Badge>}
      {r?.escribe_en_bd && <Database aria-label="escribe en BD" className="size-4 text-[var(--mis-warning)]" />}
      {r?.envia_correo && <Mail aria-label="envía correo" className="size-4 text-muted-foreground" />}
    </span>
  );
  const descripcion = ultima ? (
    <span className="flex items-center gap-2">
      <Punto tono={ESTADO_EJECUCION[ultima.estado].tono} etiqueta={ESTADO_EJECUCION[ultima.estado].texto} latido={enCurso(ultima.estado)} />
      Última ejecución: {ESTADO_EJECUCION[ultima.estado].texto.toLowerCase()} · <Hace iso={ultima.inicio} />
    </span>
  ) : "Sin ejecuciones desde la web";

  return (
    <Pagina>
      <Marco icono={<FileSpreadsheet />} titulo={encabezado} descripcion={descripcion}
        acciones={<Link href="/reportes" className={`${buttonVariants({ variant: "ghost", size: "sm" })} md:hidden`}><ArrowLeft /> Reportes</Link>}>
        {error ? (
          <ErrorEnLinea titulo="No se pudo cargar el reporte" detalle={error} onReintentar={recargar} />
        ) : cargando && !r ? (
          <EsqueletoFilas filas={5} />
        ) : r && (
          <Tabs value={pestana} onValueChange={(v) => setPestana(v as Pestana)}>
            <TabsList variant="line" className="w-full justify-start gap-4 overflow-x-auto border-b">
              <TabsTrigger value="ejecucion" className="flex-none">Ejecución</TabsTrigger>
              <TabsTrigger value="validacion" className="flex-none">Validación de tablas</TabsTrigger>
              <TabsTrigger value="archivos" className="flex-none">Archivos</TabsTrigger>
              {r.envia_correo && <TabsTrigger value="correo" className="flex-none">Correo</TabsTrigger>}
              <TabsTrigger value="historial" className="flex-none">Historial</TabsTrigger>
            </TabsList>
            <TabsContent value="ejecucion" className="pt-4">
              <PanelEjecucion reporte={r} corte={corte} onCorte={setCorte} verificacion={verificacion} onIrAValidar={() => setPestana("validacion")}
                onVerArchivos={() => setPestana("archivos")} />
            </TabsContent>
            <TabsContent value="validacion" className="pt-4">
              <PanelValidacion reporte={r} corte={corte} onCorte={setCorte} verificacion={verificacion} onVerificacion={setVerificacion} />
            </TabsContent>
            <TabsContent value="archivos" className="pt-4"><PanelArchivos reporte={r.nombre} /></TabsContent>
            {r.envia_correo && (
              <TabsContent value="correo" className="pt-4"><PanelCorreo reporte={r} corte={corte} onCorte={setCorte} /></TabsContent>
            )}
            <TabsContent value="historial" className="pt-4"><TablaEjecuciones reporte={r.nombre} /></TabsContent>
          </Tabs>
        )}
      </Marco>
    </Pagina>
  );
}
