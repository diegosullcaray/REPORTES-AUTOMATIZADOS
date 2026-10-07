"use client";

import { BookOpen, FileSpreadsheet, History, House, Settings } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Punto } from "@/components/estados";
import {
  Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupLabel, SidebarHeader, SidebarMenu, SidebarMenuBadge,
  SidebarMenuButton, SidebarMenuItem, SidebarRail,
} from "@/components/ui/sidebar";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { enCurso } from "@/lib/formato";

const PRINCIPAL = [
  { href: "/", texto: "Inicio", icono: House },
  { href: "/reportes", texto: "Reportes", icono: FileSpreadsheet },
  { href: "/ejecuciones", texto: "Ejecuciones", icono: History },
];
const SISTEMA = [{ href: "/configuracion", texto: "Configuración", icono: Settings }];

const activa = (ruta: string, href: string) => (href === "/" ? ruta === "/" : ruta.startsWith(href));

/**
 * Sidebar primario (como el de Dokploy: flotante, retráctil a íconos, grupos con etiqueta y pie con estado).
 * Muestra cuántas ejecuciones están en curso y si la API responde.
 */
export function AppSidebar() {
  const ruta = usePathname();
  const { datos, error } = useConsulta("sidebar/ejecuciones", () => api.ejecuciones(undefined, 20), () => true, 5000);
  const enMarcha = datos?.filter((x) => enCurso(x.estado)).length ?? 0;

  const menu = (items: typeof PRINCIPAL) => items.map(({ href, texto, icono: Icono }) => (
    <SidebarMenuItem key={href}>
      <SidebarMenuButton isActive={activa(ruta, href)} tooltip={texto} render={<Link href={href} />}>
        <Icono />
        <span>{texto}</span>
      </SidebarMenuButton>
      {href === "/ejecuciones" && enMarcha > 0 && <SidebarMenuBadge>{enMarcha}</SidebarMenuBadge>}
    </SidebarMenuItem>
  ));

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
          <SidebarMenu>{menu(PRINCIPAL)}</SidebarMenu>
        </SidebarGroup>
        <SidebarGroup>
          <SidebarGroupLabel>Sistema</SidebarGroupLabel>
          <SidebarMenu>{menu(SISTEMA)}</SidebarMenu>
        </SidebarGroup>
        <SidebarGroup className="group-data-[collapsible=icon]:hidden">
          <SidebarGroupLabel>Ayuda</SidebarGroupLabel>
          <SidebarMenu>
            <SidebarMenuItem>
              <SidebarMenuButton render={<a href="https://github.com/diegosullcaray/REPORTES-AUTOMATIZADOS/blob/main/governance/docs/development/runbooks/interfaz-web.md" target="_blank" rel="noopener noreferrer" />}>
                <BookOpen />
                <span>Guía de uso</span>
              </SidebarMenuButton>
            </SidebarMenuItem>
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <div className="flex items-center gap-2 rounded-md px-2 py-1.5 text-xs text-muted-foreground group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:px-0">
          <Punto tono={error ? "peligro" : datos ? "exito" : "neutro"} etiqueta={error ? "API sin conexión" : "API conectada"} latido={!error && enMarcha > 0} />
          <span className="truncate group-data-[collapsible=icon]:hidden">
            {error ? "API sin conexión" : enMarcha ? `${enMarcha} en curso` : "API conectada"}
          </span>
        </div>
      </SidebarFooter>
      <SidebarRail />
    </Sidebar>
  );
}
