"use client";

import { ChevronRight, Database, Mail, PanelLeftClose, PanelLeftOpen, Search } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useMemo, useState, useSyncExternalStore } from "react";
import { EsqueletoFilas, ErrorEnLinea } from "@/components/estados";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import {
  Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarHeader, SidebarInput, SidebarMenu,
  SidebarMenuButton, SidebarMenuItem, SidebarMenuSub, SidebarMenuSubButton, SidebarMenuSubItem,
} from "@/components/ui/sidebar";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { agruparPorCarpeta, titulo } from "@/lib/formato";
import type { ReporteResumen } from "@/lib/tipos";

const CLAVE = "sidebar-reportes-abierto";
const suscribir = (aviso: () => void) => {
  window.addEventListener("storage", aviso);
  return () => window.removeEventListener("storage", aviso);
};

/** Preferencia guardada en localStorage (sobrevive a la navegación y a recargar). */
function useAbierto(): [boolean, (v: boolean) => void] {
  const abierto = useSyncExternalStore(suscribir, () => localStorage.getItem(CLAVE) !== "no", () => true);
  return [abierto, (v) => { localStorage.setItem(CLAVE, v ? "si" : "no"); window.dispatchEvent(new Event("storage")); }];
}

const enlace = (r: ReporteResumen) => <Link href={`/reportes/${r.nombre}`} title={r.descripcion} />;

/** Un reporte: en el primer nivel (Diarios) o dentro de un nodo/carpeta (`sub`). */
function Item({ r, ruta, sub }: { r: ReporteResumen; ruta: string; sub: boolean }) {
  const contenido = (
    <>
      <span className="w-7 shrink-0 text-[11px] text-muted-foreground tabular-nums">{r.orden}</span>
      <span className="truncate">{titulo(r.nombre)}</span>
      {r.escribe_en_bd && <Database aria-label="escribe en BD" className="ml-auto size-3.5 shrink-0 text-[var(--mis-warning)]!" />}
      {r.envia_correo && <Mail aria-label="envía correo" className="ml-auto size-3.5 shrink-0" />}
    </>
  );
  const activo = ruta === `/reportes/${r.nombre}`;
  return sub ? (
    <SidebarMenuSubItem><SidebarMenuSubButton isActive={activo} render={enlace(r)}>{contenido}</SidebarMenuSubButton></SidebarMenuSubItem>
  ) : (
    <SidebarMenuItem><SidebarMenuButton isActive={activo} render={enlace(r)}>{contenido}</SidebarMenuButton></SidebarMenuItem>
  );
}

/** Carpeta del legado con varios sub-reportes (09 → 09.1, 09.2): cerrada salvo que contenga el reporte abierto. */
function Nodo({ orden, titulo: t, reportes, ruta, sub }: { orden: string; titulo: string; reportes: ReporteResumen[]; ruta: string; sub: boolean }) {
  const Elemento = sub ? SidebarMenuSubItem : SidebarMenuItem;
  return (
    <Collapsible defaultOpen={reportes.some((r) => ruta === `/reportes/${r.nombre}`)} className="group/nodo" render={<Elemento />}>
      <CollapsibleTrigger render={sub ? <SidebarMenuSubButton /> : <SidebarMenuButton />} title={t}>
        <span className="w-7 shrink-0 text-[11px] text-muted-foreground tabular-nums">{orden}</span>
        <span className="truncate">{t}</span>
        <ChevronRight className="ml-auto size-3.5 shrink-0 transition-transform duration-150 group-data-[open]/nodo:rotate-90" />
      </CollapsibleTrigger>
      <CollapsibleContent>
        <SidebarMenuSub>{reportes.map((r) => <Item key={r.nombre} r={r} ruta={ruta} sub />)}</SidebarMenuSub>
      </CollapsibleContent>
    </Collapsible>
  );
}

function Entradas({ reportes, ruta, sub }: { reportes: ReporteResumen[]; ruta: string; sub: boolean }) {
  return agruparPorCarpeta(reportes).map((e) =>
    e.tipo === "reporte"
      ? <Item key={e.r.nombre} r={e.r} ruta={ruta} sub={sub} />
      : <Nodo key={e.orden} orden={e.orden} titulo={e.titulo} reportes={e.reportes} ruta={ruta} sub={sub} />,
  );
}

function Carpeta({ titulo: t, reportes, ruta }: { titulo: string; reportes: ReporteResumen[]; ruta: string }) {
  return (
    <Collapsible defaultOpen className="group/carpeta">
      <SidebarMenuItem>
        <CollapsibleTrigger render={<SidebarMenuButton />}>
          <ChevronRight className="transition-transform duration-150 group-data-[open]/carpeta:rotate-90" />
          <span>{t}</span>
          <span className="ml-auto text-xs text-muted-foreground">{reportes.length}</span>
        </CollapsibleTrigger>
        <CollapsibleContent>
          <SidebarMenuSub>
            <Entradas reportes={reportes} ruta={ruta} sub />
          </SidebarMenuSub>
        </CollapsibleContent>
      </SidebarMenuItem>
    </Collapsible>
  );
}

/**
 * Sidebar secundario (contextual) del módulo Reportes: explorador por categoría, retráctil.
 * En el celular es la pantalla de lista (/reportes) y se oculta al abrir un reporte.
 */
export function SidebarReportes() {
  const ruta = usePathname();
  const [abierto, setAbierto] = useAbierto();
  const { datos, error, cargando, recargar } = useConsulta("reportes", api.reportes);
  const [texto, setTexto] = useState("");

  const filtrados = useMemo(() => {
    const t = texto.trim().toLowerCase();
    return (datos ?? []).filter((r) => !t || `${r.nombre} ${r.descripcion}`.toLowerCase().includes(t));
  }, [datos, texto]);
  const de = (g: string) => filtrados.filter((r) => r.grupo === g);

  const enLista = ruta === "/reportes";
  const visibilidad = enLista ? "flex w-full md:w-72" : "hidden md:flex md:w-72";

  if (!abierto) {
    return (
      <div className="sticky top-14 my-3 ml-1 hidden h-[calc(100svh-4.75rem)] w-11 shrink-0 justify-center rounded-xl border bg-sidebar pt-2 md:flex">
        <Button variant="ghost" size="icon-sm" aria-label="Mostrar lista de reportes" onClick={() => setAbierto(true)}><PanelLeftOpen /></Button>
      </div>
    );
  }

  return (
    <Sidebar collapsible="none" className={`${visibilidad} shrink-0 md:sticky md:top-14 md:my-3 md:ml-1 md:h-[calc(100svh-4.75rem)] md:rounded-xl md:border`}>
      <SidebarHeader className="gap-2">
        <div className="flex items-center justify-between px-1">
          <span className="text-sm font-semibold">Reportes</span>
          <Button variant="ghost" size="icon-sm" aria-label="Ocultar lista de reportes" onClick={() => setAbierto(false)} className="hidden md:inline-flex"><PanelLeftClose /></Button>
        </div>
        <label className="relative">
          <span className="sr-only">Buscar reporte</span>
          <Search className="pointer-events-none absolute top-1/2 left-2 size-4 -translate-y-1/2 text-muted-foreground" />
          <SidebarInput value={texto} onChange={(e) => setTexto(e.target.value)} placeholder="Buscar reporte" className="pl-8" />
        </label>
      </SidebarHeader>
      <SidebarContent>
        {error ? (
          <div className="p-2"><ErrorEnLinea titulo="No se pudo cargar el catálogo" detalle={error} onReintentar={recargar} /></div>
        ) : cargando && !datos ? (
          <div className="p-2"><EsqueletoFilas filas={10} alto="h-7" /></div>
        ) : filtrados.length === 0 ? (
          <p className="px-4 py-6 text-center text-sm text-muted-foreground">Ningún reporte coincide.</p>
        ) : (
          <>
            {de("diarias").length > 0 && (
              <SidebarGroup>
                <SidebarGroupLabel>Diarios</SidebarGroupLabel>
                <SidebarGroupContent>
                  <SidebarMenu>
                    <Entradas reportes={de("diarias")} ruta={ruta} sub={false} />
                  </SidebarMenu>
                </SidebarGroupContent>
              </SidebarGroup>
            )}
            {(de("piero").length > 0 || de("erick").length > 0) && (
              <SidebarGroup>
                <SidebarGroupLabel>Mensuales</SidebarGroupLabel>
                <SidebarGroupContent>
                  <SidebarMenu>
                    {de("piero").length > 0 && <Carpeta titulo="Heredados de Piero" reportes={de("piero")} ruta={ruta} />}
                    {de("erick").length > 0 && <Carpeta titulo="Heredados de Erick" reportes={de("erick")} ruta={ruta} />}
                  </SidebarMenu>
                </SidebarGroupContent>
              </SidebarGroup>
            )}
          </>
        )}
      </SidebarContent>
    </Sidebar>
  );
}
