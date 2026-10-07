"use client";

import { Database, Mail, Search } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useMemo, useState } from "react";
import { EsqueletoFilas, ErrorEnLinea } from "@/components/estados";
import { Input } from "@/components/ui/input";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { GRUPOS } from "@/lib/formato";
import type { Grupo } from "@/lib/tipos";

/**
 * Sidebar secundario junto al rail: catálogo de reportes agrupado por responsable del legado.
 * En el celular es la pantalla de lista (/reportes) y se oculta al abrir un reporte.
 */
export function SidebarReportes() {
  const ruta = usePathname();
  const { datos, error, cargando, recargar } = useConsulta("reportes", api.reportes);
  const [texto, setTexto] = useState("");

  const grupos = useMemo(() => {
    const t = texto.trim().toLowerCase();
    const visibles = (datos ?? []).filter((r) => !t || `${r.nombre} ${r.descripcion}`.toLowerCase().includes(t));
    return (Object.keys(GRUPOS) as Grupo[]).map((g) => ({ grupo: g, reportes: visibles.filter((r) => r.grupo === g) })).filter((g) => g.reportes.length);
  }, [datos, texto]);

  return (
    <aside aria-label="Reportes"
      className={`${ruta === "/reportes" ? "flex" : "hidden md:flex"} mis-nav-panel flex-col gap-3 rounded-[var(--mis-radius-lg)] p-3 md:fixed md:top-[var(--mis-header-h)] md:bottom-0 md:left-[var(--mis-sidebar-col1-w)] md:z-20 md:w-72 md:rounded-none`}>
      <label className="relative">
        <span className="sr-only">Buscar reporte</span>
        <Search className="pointer-events-none absolute top-1/2 left-2.5 size-4 -translate-y-1/2 text-[var(--mis-text-tertiary)]" />
        <Input value={texto} onChange={(e) => setTexto(e.target.value)} placeholder="Buscar reporte" className="pl-8" />
      </label>

      <nav className="-mx-1 flex-1 overflow-y-auto px-1">
        {error ? (
          <ErrorEnLinea titulo="No se pudo cargar el catálogo" detalle={error} onReintentar={recargar} />
        ) : cargando && !datos ? (
          <EsqueletoFilas filas={10} alto="h-9" />
        ) : grupos.length === 0 ? (
          <p className="px-2 py-6 text-center text-[13px] text-[var(--mis-text-secondary)]">Ningún reporte coincide.</p>
        ) : (
          grupos.map(({ grupo, reportes }) => (
            <section key={grupo} className="mb-3">
              <h2 className="px-2 pb-1 text-[11px] font-semibold tracking-wide text-[var(--mis-text-tertiary)] uppercase">{GRUPOS[grupo]}</h2>
              <ul className="flex flex-col gap-0.5">
                {reportes.map((r) => {
                  const activo = ruta === `/reportes/${r.nombre}`;
                  return (
                    <li key={r.nombre}>
                      <Link href={`/reportes/${r.nombre}`} aria-current={activo ? "page" : undefined} title={r.descripcion}
                        className="flex items-center gap-2 rounded-[var(--mis-radius-sm)] px-2 py-1.5 text-[13px] transition-colors duration-150 hover:bg-[var(--mis-hover-bg)] aria-[current=page]:bg-[color-mix(in_srgb,var(--mis-primary)_16%,transparent)] aria-[current=page]:font-semibold aria-[current=page]:text-[var(--mis-primary-text)]">
                        <span className="w-8 shrink-0 text-[11px] text-[var(--mis-text-tertiary)] tabular-nums">{r.orden}</span>
                        <span className="min-w-0 flex-1 truncate">{r.nombre}</span>
                        {r.escribe_en_bd && <Database aria-label="escribe en BD" className="size-3.5 shrink-0 text-[var(--mis-warning)]" />}
                        {r.envia_correo && <Mail aria-label="envía correo" className="size-3.5 shrink-0 text-[var(--mis-primary-text)]" />}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </section>
          ))
        )}
      </nav>
    </aside>
  );
}
