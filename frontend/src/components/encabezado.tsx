"use client";

import Link from "next/link";
import { usePathname, useSearchParams } from "next/navigation";
import { Fragment } from "react";
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { FiltroCierre } from "@/components/fecha-cierre";
import { Hora } from "@/components/hace";
import { ModoTema } from "@/components/modo-tema";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { GRUPOS, agruparPorCarpeta, titulo } from "@/lib/formato";

type Miga = { texto: string; href?: string };

const SECCION: Record<string, string> = { reportes: "Reportes", ejecuciones: "Ejecuciones", perfil: "Perfil", configuracion: "Configuración", servidores: "Bases de datos", validacion: "Validación de tablas" };

/** Migas según la ruta: Reportes > Diarios > Cartera sin asignar · Ejecuciones > a1b2c3… */
function useMigas(): Miga[] {
  const [seccion, id, detalle] = usePathname().split("/").filter(Boolean);
  const params = useSearchParams();
  const { datos } = useConsulta(seccion === "reportes" ? "reportes" : null, api.reportes);
  const { datos: secciones } = useConsulta(seccion === "reportes" && !id ? "secciones" : null, api.secciones);
  if (!seccion) return [{ texto: "Inicio" }];
  const raiz: Miga = { texto: SECCION[seccion] ?? seccion, href: `/${seccion}` };
  if (seccion === "reportes" && !id) { // explorador por tarjetas: /reportes?grupo=…&carpeta=…
    if (params.get("seccion")) return [raiz, { texto: secciones?.find((x) => x.id === params.get("seccion"))?.nombre ?? "Sección" }];
    const g = params.get("grupo") as keyof typeof GRUPOS | null;
    if (!g || !(g in GRUPOS)) return [{ texto: raiz.texto }];
    const nodo = agruparPorCarpeta((datos ?? []).filter((r) => r.grupo === g)).find((e) => e.tipo === "nodo" && e.reportes[0].carpeta === params.get("carpeta"));
    return nodo?.tipo === "nodo" ? [raiz, { texto: GRUPOS[g], href: `/reportes?grupo=${g}` }, { texto: `${nodo.orden} · ${nodo.titulo}` }] : [raiz, { texto: GRUPOS[g] }];
  }
  if (!id) return [{ texto: raiz.texto }];
  if (seccion === "validacion") return [raiz, { texto: id === "piero" ? "Heredados de Piero" : id === "erick" ? "Heredados de Erick" : id }];
  if (seccion === "configuracion" && id === "mcp") return detalle ? [raiz, { texto: "MCP", href: "/configuracion/mcp" }, { texto: "Google Workspace" }] : [raiz, { texto: "MCP" }];
  if (seccion === "configuracion") return [raiz, { texto: id === "notificaciones" ? "Notificaciones" : id }];
  if (seccion === "reportes") {
    const nombre = decodeURIComponent(id);
    const r = datos?.find((x) => x.nombre === nombre);
    return [raiz, ...(r ? [{ texto: GRUPOS[r.grupo], href: `/reportes?grupo=${r.grupo}` }] : []), { texto: titulo(nombre) }];
  }
  return [raiz, { texto: `Ejecución ${id.slice(0, 8)}` }];
}

export function Encabezado() {
  const migas = useMigas();
  return (
    <header className="sticky top-0 z-20 flex h-14 shrink-0 items-center gap-2 bg-background/80 px-4 backdrop-blur transition-[height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
      <SidebarTrigger className="-ml-1 mr-1" />
      <Breadcrumb className="min-w-0 flex-1">
        <BreadcrumbList>
          {migas.map((m, i) => (
            <Fragment key={i}>
              {i > 0 && <BreadcrumbSeparator className="hidden sm:inline-flex" />}
              <BreadcrumbItem className={i < migas.length - 1 ? "hidden sm:inline-flex" : "min-w-0"}>
                {i === migas.length - 1 ? (
                  <BreadcrumbPage className="truncate">{m.texto}</BreadcrumbPage>
                ) : m.href ? (
                  <BreadcrumbLink render={<Link href={m.href} />}>{m.texto}</BreadcrumbLink>
                ) : (
                  <span>{m.texto}</span>
                )}
              </BreadcrumbItem>
            </Fragment>
          ))}
        </BreadcrumbList>
      </Breadcrumb>
      <FiltroCierre />
      <Hora />
      <ModoTema />
    </header>
  );
}
