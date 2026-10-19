"use client";

import type { LucideIcon } from "lucide-react";
import { BookOpen, FileText, Play, Bell, Bot, Tag, ChevronRight, ChevronsUpDown, FileSpreadsheet, History, House, LogOut, Plug, ShieldCheck, SlidersHorizontal, UserRound } from "lucide-react";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { Avatar, AvatarBadge, AvatarFallback } from "@/components/ui/avatar";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuGroup, DropdownMenuItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupLabel, SidebarHeader, SidebarMenu, SidebarMenuAction,
  SidebarMenuBadge, SidebarMenuButton, SidebarMenuItem, SidebarMenuSub, SidebarMenuSubButton, SidebarMenuSubItem, SidebarRail, useSidebar,
} from "@/components/ui/sidebar";
import { ModoTema } from "@/components/modo-tema";
import { useConsulta } from "@/hooks/use-consulta";
import { api, irALogin } from "@/lib/api";
import { useAvatar } from "@/hooks/use-avatar";
import { enCurso, iniciales } from "@/lib/formato";
import { cn } from "@/lib/utils";

/** Ítem plano del menú (como los de Home/Settings de Dokploy): fondo `bg-border` y ícono de marca cuando la ruta está activa. */
function Item({ destino, texto, icono: Icono, activo, insignia }: { destino: string; texto: string; icono: LucideIcon; activo: boolean; insignia?: number }) {
  return (
    <SidebarMenuItem>
      <SidebarMenuButton isActive={activo} tooltip={texto} className={cn(activo && "bg-border")} render={<Link href={destino} prefetch={false} />}>
        <Icono className={cn(activo && "text-[var(--mis-primary-text)]")} /><span>{texto}</span>
      </SidebarMenuButton>
      {!!insignia && <SidebarMenuBadge>{insignia}</SidebarMenuBadge>}
    </SidebarMenuItem>
  );
}

/** «Validación de tablas» como menú plegable: la tabla general y una pantalla por responsable. */
function MenuValidacion({ ruta }: { ruta: string }) {
  const [elegido, setElegido] = useState<boolean | null>(null); // null = abierto mientras estés en Validación
  return (
    <Collapsible open={elegido ?? ruta.startsWith("/validacion")} onOpenChange={setElegido} className="group/validacion" render={<SidebarMenuItem />}>
      <SidebarMenuButton isActive={ruta === "/validacion"} tooltip="Validación de tablas" render={<Link href="/validacion" />}>
        <ShieldCheck />
        <span>Validación de tablas</span>
      </SidebarMenuButton>
      <CollapsibleTrigger render={<SidebarMenuAction aria-label="Mostrar u ocultar los responsables" />}>
        <ChevronRight className="transition-transform duration-150 group-data-[open]/validacion:rotate-90" />
      </CollapsibleTrigger>
      <CollapsibleContent>
        <SidebarMenuSub>
          {([["piero", "Heredados de Piero"], ["erick", "Heredados de Erick"]] as const).map(([grupo, texto]) => (
            <SidebarMenuSubItem key={grupo}>
              <SidebarMenuSubButton isActive={ruta.startsWith(`/validacion/${grupo}`)} render={<Link href={`/validacion/${grupo}`} prefetch={false} />}>
                <span className="truncate">{texto}</span>
              </SidebarMenuSubButton>
            </SidebarMenuSubItem>
          ))}
        </SidebarMenuSub>
      </CollapsibleContent>
    </Collapsible>
  );
}

/** Módulo Diccionario: el diccionario de datos de los reportes MIS (repo DICCIONARIO). */
const DICCIONARIO = [
  { ruta: "/diccionario", texto: "Resumen", icono: BookOpen },
  { ruta: "/diccionario/reportes", texto: "Reportes del MIS", icono: FileText },
  { ruta: "/diccionario/procesos", texto: "Procesos", icono: Play },
] as const;

/** Páginas de ajustes, cada una con su ruta (como los ítems de Settings en Dokploy). */
const AJUSTES = [
  { ruta: "/configuracion", texto: "General", icono: SlidersHorizontal },
  { ruta: "/configuracion/notificaciones", texto: "Notificaciones", icono: Bell },
  { ruta: "/configuracion/mcp", texto: "MCP", icono: Plug },
  { ruta: "/configuracion/ia", texto: "Inteligencia artificial", icono: Bot },
  { ruta: "/configuracion/etiquetas", texto: "Etiquetas", icono: Tag },
] as const;

/** Menú de usuario en el pie (como el UserNav de Dokploy): perfil, configuración y estado de la API. */
function MenuUsuario({ enMarcha, apiCaida }: { enMarcha: number; apiCaida: boolean }) {
  const router = useRouter();
  const { isMobile } = useSidebar();
  const { datos: sesion } = useConsulta("sesion", api.sesion);
  const usuario = sesion?.usuario ?? "…";
  const color = useAvatar();
  return (
    <DropdownMenu>
      <DropdownMenuTrigger render={<SidebarMenuButton size="lg" className="data-popup-open:bg-sidebar-accent" />}>
        <Avatar>
          <AvatarFallback style={color ? { background: color } : undefined} className="bg-primary text-xs font-semibold text-primary-foreground">{iniciales(usuario)}</AvatarFallback>
          <AvatarBadge aria-label={apiCaida ? "API sin conexión" : "API conectada"} className={`ring-sidebar ${apiCaida ? "bg-[var(--mis-danger)]" : "bg-[var(--mis-success)]"} ${!apiCaida && enMarcha > 0 ? "animate-pulse" : ""}`} />
        </Avatar>
        <span className="grid flex-1 text-left text-sm leading-tight">
          <span className="truncate font-semibold">{usuario}</span>
          <span className="truncate text-xs text-sidebar-foreground/60">{apiCaida ? "API sin conexión" : enMarcha ? `${enMarcha} en curso` : "API conectada"}</span>
        </span>
        <ChevronsUpDown className="ml-auto size-4" />
      </DropdownMenuTrigger>
      <DropdownMenuContent side={isMobile ? "bottom" : "right"} align="end" sideOffset={4} className="min-w-56 rounded-lg">
        <div className="flex items-center justify-between px-2 py-1.5">
          <DropdownMenuGroup>
            <DropdownMenuLabel className="flex flex-col">
              Mi cuenta
              <span className="text-xs font-normal text-muted-foreground">{usuario}</span>
            </DropdownMenuLabel>
          </DropdownMenuGroup>
          <ModoTema />
        </div>
        <DropdownMenuSeparator />
        <DropdownMenuGroup>
          <DropdownMenuItem onClick={() => router.push("/perfil")}><UserRound /> Perfil</DropdownMenuItem>
        </DropdownMenuGroup>
        <DropdownMenuSeparator />
        <DropdownMenuItem onClick={() => api.cerrarSesion().finally(irALogin)}><LogOut /> Cerrar sesión</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

/** Sidebar principal (como el de Dokploy): flotante, retráctil a íconos, con ítems planos (Principal y Configuración) y el menú de usuario al pie. */
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
                <span className="text-xs text-sidebar-foreground/60">Financiera Confianza</span>
              </span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Principal</SidebarGroupLabel>
          <SidebarMenu>
            <Item destino="/" texto="Inicio" icono={House} activo={ruta === "/"} />
            <Item destino="/reportes" texto="Reportes" icono={FileSpreadsheet} activo={ruta.startsWith("/reportes")} />
            <MenuValidacion ruta={ruta} />
            <Item destino="/ejecuciones" texto="Ejecuciones" icono={History} activo={ruta.startsWith("/ejecuciones")} insignia={enMarcha} />
          </SidebarMenu>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupLabel>Diccionario</SidebarGroupLabel>
          <SidebarMenu className="gap-1">
            {DICCIONARIO.map(({ ruta: destino, texto, icono }) => (
              <Item key={destino} destino={destino} texto={texto} icono={icono} activo={destino === "/diccionario" ? ruta === destino : ruta.startsWith(destino) || (destino === "/diccionario/reportes" && ruta.startsWith("/diccionario/tablas"))} />
            ))}
          </SidebarMenu>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupLabel>Configuración</SidebarGroupLabel>
          <SidebarMenu className="gap-1">
            {AJUSTES.map(({ ruta: destino, texto, icono }) => (
              <Item key={destino} destino={destino} texto={texto} icono={icono} activo={ruta === destino || (destino !== "/configuracion" && ruta.startsWith(`${destino}/`))} />
            ))}
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
