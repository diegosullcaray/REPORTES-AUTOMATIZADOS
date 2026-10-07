"use client";

import { FileSpreadsheet, History, Moon, PlugZap, Sun } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const SECCIONES = [
  { href: "/reportes", texto: "Reportes", icono: FileSpreadsheet, activa: (p: string) => p === "/" || p.startsWith("/reportes") },
  { href: "/ejecuciones", texto: "Historial", icono: History, activa: (p: string) => p.startsWith("/ejecuciones") },
  { href: "/conexiones", texto: "Conexión", icono: PlugZap, activa: (p: string) => p.startsWith("/conexiones") },
];

/** Rail navy de MIS: columna a la izquierda en escritorio, barra abajo en el celular. */
export function Rail() {
  const ruta = usePathname();
  return (
    <nav aria-label="Secciones"
      className="mis-rail fixed inset-x-0 bottom-0 z-40 flex h-16 justify-around md:inset-y-0 md:left-0 md:right-auto md:h-auto md:w-[var(--mis-sidebar-col1-w)] md:flex-col md:justify-start md:gap-2 md:pt-3">
      {SECCIONES.map(({ href, texto, icono: Icono, activa }) => (
        <Link key={href} href={href} aria-current={activa(ruta) ? "page" : undefined}
          className="mis-rail-item mx-1 my-1.5 flex flex-1 flex-col items-center justify-center gap-1 rounded-[var(--mis-radius-md)] px-0 py-1.5 md:flex-none">
          <Icono className="size-5" />
          <span className="max-w-full truncate text-[var(--mis-text-xs)] leading-none md:text-[10px]">{texto}</span>
        </Link>
      ))}
    </nav>
  );
}

/** El tema vive en la clase `.dark` de <html> (como en MIS); el ícono lo decide el CSS, sin estado. */
export function BotonTema() {
  const cambiar = () => {
    const oscuro = document.documentElement.classList.toggle("dark");
    localStorage.setItem("tema", oscuro ? "oscuro" : "claro");
  };
  return (
    <button onClick={cambiar} aria-label="Cambiar tema claro/oscuro"
      className="flex size-9 items-center justify-center rounded-full border transition-colors duration-150"
      style={{ background: "var(--mis-header-control-bg)", borderColor: "var(--mis-header-control-border)" }}>
      <Moon className="size-4 dark:hidden" />
      <Sun className="hidden size-4 dark:block" />
    </button>
  );
}

/** Se ejecuta antes de pintar: evita el destello claro→oscuro. */
export const SCRIPT_TEMA = `try{if(localStorage.getItem("tema")==="oscuro")document.documentElement.classList.add("dark")}catch(e){}`;
