"use client";

import { ArrowLeft, Database, Mail } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { Chip, EsqueletoFilas, ErrorEnLinea } from "@/components/estados";
import { buttonVariants } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Ventana } from "@/components/ventana";
import { TablaEjecuciones } from "@/features/ejecuciones/tabla-ejecuciones";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { GRUPOS } from "@/lib/formato";
import type { Verificacion } from "@/lib/tipos";
import { PanelArchivos } from "./panel-archivos";
import { PanelCorreo } from "./panel-correo";
import { PanelEjecucion } from "./panel-ejecucion";
import { PanelValidacion } from "./panel-validacion";

type Pestana = "validar" | "ejecutar" | "archivos" | "correo" | "historial";

/** Orquesta el procedimiento del runbook: 1 validar tablas → 2 ejecutar → 3 revisar archivos → 4 correo. */
export function DetalleReporte({ nombre }: { nombre: string }) {
  const { datos: r, error, cargando, recargar } = useConsulta(`reporte/${nombre}`, () => api.reporte(nombre));
  const [pestana, setPestana] = useState<Pestana>("validar");
  const [elegido, setCorte] = useState<string | null>(null); // null = la fecha por defecto del reporte
  const [verificacion, setVerificacion] = useState<Verificacion | null>(null);
  const corte = elegido ?? r?.corte.fecha ?? "";

  // En escritorio el sidebar ya es la navegación; en el celular hace falta volver a la lista.
  const volver = <Link href="/reportes" className={`${buttonVariants({ variant: "ghost", size: "sm" })} md:hidden`}><ArrowLeft /> Reportes</Link>;

  return (
    <Ventana titulo={nombre} acciones={volver}>
      {error ? (
        <ErrorEnLinea titulo="No se pudo cargar el reporte" detalle={error} onReintentar={recargar} />
      ) : cargando && !r ? (
        <EsqueletoFilas filas={5} />
      ) : r && (
        <>
          <header className="flex flex-col gap-2">
            <p className="text-[var(--mis-text-secondary)]">{r.descripcion}</p>
            <div className="flex flex-wrap gap-1">
              <Chip>{GRUPOS[r.grupo]} {r.orden}</Chip>
              <Chip tono={r.frecuencia === "diaria" ? "info" : "neutro"}>{r.frecuencia}</Chip>
              <Chip>servidor {r.servidores.join(", ")}</Chip>
              {r.escribe_en_bd && <Chip tono="aviso"><Database className="size-3" />escribe en BD</Chip>}
              {r.envia_correo && <Chip tono="info"><Mail className="size-3" />envía correo</Chip>}
              {r.vacio_valido && <Chip>vacío es válido</Chip>}
            </div>
          </header>

          <Tabs value={pestana} onValueChange={(v) => setPestana(v as Pestana)}>
            <TabsList variant="line" className="mis-pestanas w-full justify-start">
              <TabsTrigger value="validar" className="flex-none">1. Validar tablas</TabsTrigger>
              <TabsTrigger value="ejecutar" className="flex-none">2. Ejecutar</TabsTrigger>
              <TabsTrigger value="archivos" className="flex-none">3. Archivos</TabsTrigger>
              {r.envia_correo && <TabsTrigger value="correo" className="flex-none">4. Correo</TabsTrigger>}
              <TabsTrigger value="historial" className="flex-none">Historial</TabsTrigger>
            </TabsList>
            <TabsContent value="validar" className="pt-3">
              <PanelValidacion reporte={r} corte={corte} onCorte={setCorte} verificacion={verificacion} onVerificacion={setVerificacion} />
            </TabsContent>
            <TabsContent value="ejecutar" className="pt-3">
              <PanelEjecucion reporte={r} corte={corte} onCorte={setCorte} verificacion={verificacion} onIrAValidar={() => setPestana("validar")} />
            </TabsContent>
            <TabsContent value="archivos" className="pt-3"><PanelArchivos reporte={r.nombre} /></TabsContent>
            {r.envia_correo && (
              <TabsContent value="correo" className="pt-3"><PanelCorreo reporte={r} corte={corte} onCorte={setCorte} /></TabsContent>
            )}
            <TabsContent value="historial" className="pt-3"><TablaEjecuciones reporte={r.nombre} /></TabsContent>
          </Tabs>
        </>
      )}
    </Ventana>
  );
}
