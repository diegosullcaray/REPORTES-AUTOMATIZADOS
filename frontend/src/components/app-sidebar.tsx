"use client";

import { ChevronRight, ChevronsUpDown, Database, FileSpreadsheet, History, House, LogOut, Mail, Monitor, Moon, SlidersHorizontal, Sun, UserRound } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useTheme } from "next-themes";
import { useState } from "react";
import { Punto } from "@/components/estados";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuGroup, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupLabel, SidebarHeader, SidebarMenu, SidebarMenuAction,
  SidebarMenuBadge, SidebarMenuButton, SidebarMenuItem, SidebarMenuSub, SidebarMenuSubButton, SidebarMenuSubItem, SidebarRail,
} from "@/components/ui/sidebar";
import { useConsulta } from "@/hooks/use-consulta";
import { api, irALogin } from "@/lib/api";
import { agruparPorCarpeta, enCurso, iniciales, titulo } from "@/lib/formato";
import type { ReporteResumen } from "@/lib/tipos";

// Sin precarga: el árbol muestra hasta 22 enlaces a la vez y precargarlos todos satura el servidor de Next.
const enlace = (r: ReporteResumen) => <Link href={`/reportes/${r.nombre}`} title={r.descripcion} prefetch={false} />;
const rutaDe = (r: ReporteResumen) => `/reportes/${r.nombre}`;

function Hoja({ r, ruta }: { r: ReporteResumen; ruta: string }) {
  return (
    <SidebarMenuSubItem>
      <SidebarMenuSubButton isActive={ruta === rutaDe(r)} render={enlace(r)}>
        <span className="w-7 shrink-0 text-[11px] text-muted-foreground tabular-nums">{r.orden}</span>
        <span className="truncate">{titulo(r.nombre)}</span>
        {r.escribe_en_bd && <Database aria-label="escribe en BD" className="ml-auto size-3.5 shrink-0 text-[var(--mis-warning)]!" />}
        {r.envia_correo && <Mail aria-label="envía correo" className="ml-auto size-3.5 shrink-0" />}
      </SidebarMenuSubButton>
    </SidebarMenuSubItem>
  );
}

/** Carpeta plegable dentro del árbol: categoría (Diarios, Piero, Erick) o carpeta del legado con sub-reportes (09 → 09.1, 09.2). */
function Carpeta({ etiqueta, orden, reportes, ruta, abierta }: { etiqueta: string; orden?: string; reportes: ReporteResumen[]; ruta: string; abierta?: boolean }) {
  const contieneActivo = reportes.some((r) => ruta === rutaDe(r));
  const [elegido, setElegido] = useState<boolean | null>(null); // null = sigue a la ruta hasta que el usuario la pliegue o despliegue
  return (
    <Collapsible open={elegido ?? (!!abierta || contieneActivo)} onOpenChange={setElegido} className="group/carpeta" render={<SidebarMenuSubItem />}>
      {/* SidebarMenuSubButton es un <a> por defecto; para plegar hace falta un <button> real (teclado y lectores de pantalla). */}
      <CollapsibleTrigger render={<SidebarMenuSubButton render={<button type="button" />} />} title={etiqueta}>
        {orden && <span className="w-7 shrink-0 text-[11px] text-muted-foreground tabular-nums">{orden}</span>}
        <span className="truncate">{etiqueta}</span>
        <ChevronRight className="ml-auto size-3.5 shrink-0 transition-transform duration-150 group-data-[open]/carpeta:rotate-90" />
      </CollapsibleTrigger>
      <CollapsibleContent>
        <SidebarMenuSub className="mr-0 pr-0">
          {/* Una carpeta del legado (con `orden`) ya es un grupo: sus reportes van directo; agruparla de nuevo no termina nunca. */}
          {orden ? reportes.map((r) => <Hoja key={r.nombre} r={r} ruta={ruta} />)
            : agruparPorCarpeta(reportes).map((e) => e.tipo === "reporte"
              ? <Hoja key={e.r.nombre} r={e.r} ruta={ruta} />
              : <Carpeta key={e.orden} etiqueta={e.titulo} orden={e.orden} reportes={e.reportes} ruta={ruta} />)}
        </SidebarMenuSub>
      </CollapsibleContent>
    </Collapsible>
  );
}

/** «Reportes» como menú plegable del sidebar principal (como los ítems con sub-menú de Dokploy). */
function MenuReportes({ ruta }: { ruta: string }) {
  const { datos } = useConsulta("reportes", api.reportes);
  const de = (g: string) => datos?.filter((r) => r.grupo === g) ?? [];
  const [elegido, setElegido] = useState<boolean | null>(null); // null = abierto mientras estés en Reportes
  return (
    <Collapsible open={elegido ?? ruta.startsWith("/reportes")} onOpenChange={setElegido} className="group/reportes" render={<SidebarMenuItem />}>
      <SidebarMenuButton isActive={ruta === "/reportes"} tooltip="Reportes" render={<Link href="/reportes" />}>
        <FileSpreadsheet />
        <span>Reportes</span>
      </SidebarMenuButton>
      <CollapsibleTrigger render={<SidebarMenuAction aria-label="Mostrar u ocultar la lista de reportes" />}>
        <ChevronRight className="transition-transform duration-150 group-data-[open]/reportes:rotate-90" />
      </CollapsibleTrigger>
      <CollapsibleContent>
        {/* Las carpetas se montan con el catálogo ya cargado: así ven desde el inicio qué reporte está abierto. */}
        {datos && (
          <SidebarMenuSub>
            <Carpeta etiqueta="Diarios" reportes={de("diarias")} ruta={ruta} abierta />
            <Carpeta etiqueta="Heredados de Piero" reportes={de("piero")} ruta={ruta} />
            <Carpeta etiqueta="Heredados de Erick" reportes={de("erick")} ruta={ruta} />
          </SidebarMenuSub>
        )}
      </CollapsibleContent>
    </Collapsible>
  );
}

/** Menú de usuario en el pie (como el UserNav de Dokploy): perfil, configuración, tema y estado de la API. */
function MenuUsuario({ enMarcha, apiCaida }: { enMarcha: number; apiCaida: boolean }) {
  const router = useRouter();
  const { datos: p } = useConsulta("perfil", api.perfil);
  const { resolvedTheme, setTheme } = useTheme();
  const usuario = p?.usuario ?? "…";
  return (
    <DropdownMenu>
      <DropdownMenuTrigger render={<SidebarMenuButton size="lg" className="data-popup-open:bg-sidebar-accent" />}>
        <span className="relative flex size-8 shrink-0 items-center justify-center rounded-lg bg-primary text-xs font-semibold text-primary-foreground">
          {iniciales(usuario)}
          <span className="absolute -right-0.5 -bottom-0.5 rounded-full ring-2 ring-sidebar">
            <Punto tono={apiCaida ? "peligro" : "exito"} etiqueta={apiCaida ? "API sin conexión" : "API conectada"} latido={!apiCaida && enMarcha > 0} />
          </span>
        </span>
        <span className="grid flex-1 text-left text-sm leading-tight">
          <span className="truncate font-semibold">{usuario}</span>
          <span className="truncate text-xs text-muted-foreground">{apiCaida ? "API sin conexión" : enMarcha ? `${enMarcha} en curso` : "API conectada"}</span>
        </span>
        <ChevronsUpDown className="ml-auto size-4" />
      </DropdownMenuTrigger>
      <DropdownMenuContent side="top" align="start" className="w-64">
        <DropdownMenuGroup>
          <DropdownMenuLabel className="flex flex-col">
            Mi cuenta
            <span className="text-xs font-normal text-muted-foreground">{p ? `${p.usuario} · ${p.equipo}` : "…"}</span>
          </DropdownMenuLabel>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem onClick={() => router.push("/perfil")}><UserRound /> Perfil</DropdownMenuItem>
          <DropdownMenuItem onClick={() => router.push("/perfil?seccion=general")}><SlidersHorizontal /> Configuración</DropdownMenuItem>
          <DropdownMenuItem onClick={() => router.push("/perfil?seccion=bases")}><Database /> Bases de datos</DropdownMenuItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuLabel>Tema</DropdownMenuLabel>
          <DropdownMenuItem onClick={() => setTheme("light")}><Sun /> Claro {resolvedTheme === "light" && "✓"}</DropdownMenuItem>
          <DropdownMenuItem onClick={() => setTheme("dark")}><Moon /> Oscuro {resolvedTheme === "dark" && "✓"}</DropdownMenuItem>
          <DropdownMenuItem onClick={() => setTheme("system")}><Monitor /> Como el sistema</DropdownMenuItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => api.cerrarSesion().finally(irALogin)}><LogOut /> Cerrar sesión</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

/** Sidebar principal (como el de Dokploy): flotante, retráctil a íconos, con el árbol de reportes y el menú de usuario al pie. */
export function AppSidebar() {
  const ruta = usePathname();
  const { datos, error } = useConsulta("sidebar/ejecuciones", () => api.ejecuciones(undefined, 20), () => true, 5000);
  const enMarcha = datos?.filter((x) => enCurso(x.estado)).length ?? 0;

  return (
    <Sidebar collapsible="icon" variant="floating">
      <SidebarHeader>
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton size="lg" render={<Link href="/" />}>
              <span className="flex aspect-square size-8 items-center justify-center rounded-md bg-sidebar-primary text-xs font-bold text-sidebar-primary-foreground">MIS</span>
              <span className="flex flex-col leading-tight">
                <span className="font-semibold">Reportes automatizados</span>
                <span className="text-xs text-muted-foreground">Financiera Confianza</span>
              </span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Principal</SidebarGroupLabel>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton isActive={ruta === "/"} tooltip="Inicio" render={<Link href="/" />}><House /><span>Inicio</span></SidebarMenuButton>
            </SidebarMenuItem>
            <MenuReportes ruta={ruta} />
            <SidebarMenuItem>
              <SidebarMenuButton isActive={ruta.startsWith("/ejecuciones")} tooltip="Ejecuciones" render={<Link href="/ejecuciones" />}><History /><span>Ejecuciones</span></SidebarMenuButton>
              {enMarcha > 0 && <SidebarMenuBadge>{enMarcha}</SidebarMenuBadge>}
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <SidebarMenu>
          <SidebarMenuItem><MenuUsuario enMarcha={enMarcha} apiCaida={!!error} /></SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
