"use client";

import { Moon, Sun } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTheme } from "next-themes";
import { Fragment } from "react";
import {
  Breadcrumb, BreadcrumbItem, BreadcrumbLink, BreadcrumbList, BreadcrumbPage, BreadcrumbSeparator,
} from "@/components/ui/breadcrumb";
import { Hora } from "@/components/hace";
import { Button } from "@/components/ui/button";
import { SidebarTrigger } from "@/components/ui/sidebar";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { CATEGORIA, titulo } from "@/lib/formato";

type Miga = { texto: string; href?: string };

const SECCION: Record<string, string> = { reportes: "Reportes", ejecuciones: "Ejecuciones", configuracion: "Configuración" };

/** Migas según la ruta: Reportes > Diarios > Cartera sin asignar · Ejecuciones > a1b2c3… */
function useMigas(): Miga[] {
  const [seccion, id] = usePathname().split("/").filter(Boolean);
  const { datos } = useConsulta(seccion === "reportes" && id ? "reportes" : null, api.reportes);
  if (!seccion) return [{ texto: "Inicio" }];
  const raiz: Miga = { texto: SECCION[seccion] ?? seccion, href: `/${seccion}` };
  if (!id) return [{ texto: raiz.texto }];
  if (seccion === "reportes") {
    const nombre = decodeURIComponent(id);
    const r = datos?.find((x) => x.nombre === nombre);
    return [raiz, ...(r ? [{ texto: CATEGORIA[r.frecuencia] }] : []), { texto: titulo(nombre) }];
  }
  return [raiz, { texto: `Ejecución ${id.slice(0, 8)}` }];
}

export function Encabezado() {
  const migas = useMigas();
  const { resolvedTheme, setTheme } = useTheme();
  return (
    <header className="sticky top-0 z-20 flex h-14 shrink-0 items-center gap-2 bg-background/80 px-4 backdrop-blur transition-[height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
      <SidebarTrigger className="-ml-1 mr-1" />
      <Breadcrumb className="min-w-0 flex-1">
        <BreadcrumbList>
          {migas.map((m, i) => (
            <Fragment key={i}>
              {i > 0 && <BreadcrumbSeparator />}
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
      <Hora />
      <Button variant="ghost" size="icon" aria-label="Cambiar tema claro/oscuro" onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}>
        <Moon className="dark:hidden" />
        <Sun className="hidden dark:block" />
      </Button>
    </header>
  );
}
