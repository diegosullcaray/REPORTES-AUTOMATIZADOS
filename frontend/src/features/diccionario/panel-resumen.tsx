"use client";

import { BookOpen } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useMemo } from "react";
import { Aviso, ErrorEnLinea, EsqueletoFilas } from "@/components/estados";
import { Grafico, type Colores } from "@/components/grafico";
import { Hace } from "@/components/hace";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Tarjeta } from "@/components/tarjeta";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import type { DicBase, DicDatos, DicHallazgo, DicOrigenCatalogo, DicPotencial } from "@/lib/tipos";
import { avancePorBase, porRegla } from "./calidad";
import { EnlaceTabla, enlaceTabla } from "./comun";

const EJES = (c: Colores) => ({ axisLine: { show: false }, axisTick: { show: false }, axisLabel: { color: c.tenue }, splitLine: { lineStyle: { color: c.linea } } });

/** Cuánto de los procedimientos de cada base está validado, extraído sin validar o pendiente (en %, para que una base chica se vea igual que una grande). */
function Avance({ bases }: { bases: DicBase[] }) {
  const con = useMemo(() => avancePorBase(bases), [bases]);
  const opcion = useMemo(() => (c: Colores) => {
    const serie = (name: string, pct: "pctValidados" | "pctExtraidos" | "pctPendientes", n: "validados" | "extraidos" | "pendientes", color: string, texto: string) => ({
      name, type: "bar", stack: "sp", data: con.map((b) => ({ value: b[pct], n: b[n] })), itemStyle: { color }, barMaxWidth: 28, emphasis: { focus: "series" },
      label: { show: true, color: texto, formatter: (p: { data: { n: number } }) => (p.data.n ? String(p.data.n) : "") },
    });
    return {
      grid: { left: 8, right: 16, top: 36, bottom: 4, containLabel: true },
      legend: { top: 0, left: 0, textStyle: { color: c.tenue }, itemWidth: 12, itemHeight: 12 },
      tooltip: {
        trigger: "axis", axisPointer: { type: "shadow" },
        formatter: (ps: { name: string; seriesName: string; data: { n: number } }[]) => `${ps[0].name}<br/>${ps.map((p) => `${p.seriesName}: ${p.data.n}`).join("<br/>")}`,
      },
      xAxis: { type: "value", max: 100, ...EJES(c), axisLabel: { color: c.tenue, formatter: "{value}%" } },
      yAxis: { type: "category", inverse: true, data: con.map((b) => b.base), axisLine: { lineStyle: { color: c.linea } }, axisTick: { show: false }, axisLabel: { color: c.texto } },
      series: [
        serie("Validados", "pctValidados", "validados", c.marca, c.superficie),
        serie("Extraídos, sin validar", "pctExtraidos", "extraidos", c.c("color-mix(in srgb, var(--mis-primary) 50%, var(--mis-surface))"), c.texto),
        serie("Pendientes de extraer", "pctPendientes", "pendientes", c.c("color-mix(in srgb, var(--mis-primary) 14%, var(--mis-surface))"), c.texto),
      ],
    };
  }, [con]);
  return (
    <Grafico opcion={opcion} alto={Math.max(160, con.length * 56 + 48)}
      resumen={`Procedimientos por base: ${con.map((b) => `${b.base} ${b.validados} de ${b.total} validados`).join("; ")}.`}
      tabla={{ columnas: ["Base", "Validados", "Extraídos", "Procedimientos"], filas: con.map((b) => [b.base, b.validados, b.validados + b.extraidos, b.total]) }} />
  );
}

/** Errores y avisos por regla de calidad (lo informativo no se muestra: no pide acción). */
function Calidad({ hallazgos }: { hallazgos: DicHallazgo[] }) {
  const reglas = useMemo(() => porRegla(hallazgos), [hallazgos]);
  const opcion = useMemo(() => (c: Colores) => {
    const serie = (name: string, data: number[], color: string) => ({ name, type: "bar", stack: "n", data, itemStyle: { color }, barMaxWidth: 22, label: { show: true, color: c.superficie, formatter: (p: { value: number }) => (p.value ? String(p.value) : "") } });
    return {
      grid: { left: 8, right: 16, top: 36, bottom: 4, containLabel: true },
      legend: { top: 0, left: 0, textStyle: { color: c.tenue }, itemWidth: 12, itemHeight: 12 },
      tooltip: { trigger: "axis", axisPointer: { type: "shadow" } },
      xAxis: { type: "value", ...EJES(c) },
      yAxis: { type: "category", inverse: true, data: reglas.map(([r]) => r), axisLine: { lineStyle: { color: c.linea } }, axisTick: { show: false }, axisLabel: { color: c.texto, width: 150, overflow: "break" } },
      series: [serie("Errores", reglas.map(([, n]) => n.error), c.peligro), serie("Avisos", reglas.map(([, n]) => n.aviso), c.aviso)],
    };
  }, [reglas]);
  if (!reglas.length) return <p className="text-sm text-muted-foreground">Sin errores ni avisos.</p>;
  return (
    <Grafico opcion={opcion} alto={Math.max(160, reglas.length * 40 + 48)}
      resumen={`Hallazgos por regla: ${reglas.map(([r, n]) => `${r} ${n.error} errores y ${n.aviso} avisos`).join("; ")}.`}
      tabla={{ columnas: ["Regla", "Errores", "Avisos"], filas: reglas.map(([r, n]) => [r, n.error, n.aviso]) }} />
  );
}

/** Las tablas que más reportes del MIS leen y que tus reportes aún no usan: se pulsa una barra para abrirla. */
function Candidatas({ p }: { p: DicPotencial }) {
  const router = useRouter();
  const top = useMemo(() => p.disponibles.slice(0, 10), [p.disponibles]);
  const opcion = useMemo(() => (c: Colores) => ({
    grid: { left: 8, right: 36, top: 4, bottom: 4, containLabel: true },
    tooltip: { trigger: "axis", axisPointer: { type: "shadow" }, valueFormatter: (v: number) => `${v} reportes del MIS` },
    xAxis: { type: "value", ...EJES(c) },
    yAxis: { type: "category", inverse: true, data: top.map((t) => t.nombre), axisLine: { lineStyle: { color: c.linea } }, axisTick: { show: false }, axisLabel: { color: c.texto } },
    series: [{ type: "bar", data: top.map((t) => t.reportes_mis), itemStyle: { color: c.marca }, barMaxWidth: 20, label: { show: true, position: "right", color: c.tenue } }],
  }), [top]);
  if (!top.length) return <p className="text-sm text-muted-foreground">Tus reportes ya usan todas las tablas del diccionario.</p>;
  return (
    <Grafico opcion={opcion} alto={top.length * 32 + 24} alClic={(nombre) => router.push(enlaceTabla(nombre))}
      resumen={`Tablas que más reportes del MIS leen: ${top.map((t) => `${t.nombre} ${t.reportes_mis}`).join("; ")}.`}
      tabla={{ columnas: ["Tabla", "Reportes del MIS", "Fechas"], filas: top.map((t) => [t.nombre, t.reportes_mis, t.fechas.join(", ") || "—"]) }} />
  );
}

/** Cuántas de las tablas de tus reportes tienen ficha en el diccionario. */
function Cobertura({ p }: { p: DicPotencial }) {
  const pct = p.tablas_registradas ? Math.round((p.en_diccionario / p.tablas_registradas) * 100) : 0;
  return (
    <div className="flex flex-col gap-2">
      <div className="flex items-baseline justify-between gap-3">
        <span className="text-sm"><b className="text-2xl font-semibold tabular-nums">{p.en_diccionario}</b> de {p.tablas_registradas} tablas de tus reportes están en el diccionario</span>
        <span className="text-sm text-muted-foreground tabular-nums">{pct} %</span>
      </div>
      <div role="meter" aria-valuenow={p.en_diccionario} aria-valuemin={0} aria-valuemax={p.tablas_registradas} aria-label="Cobertura del diccionario sobre tus tablas"
        className="h-2.5 overflow-hidden rounded-full" style={{ background: "color-mix(in srgb, var(--mis-primary) 14%, var(--mis-surface))" }}>
        <div className="h-full rounded-full" style={{ width: `${pct}%`, background: "var(--mis-primary)" }} />
      </div>
      {p.faltan_en_diccionario.length > 0 && (
        <details className="text-xs text-muted-foreground">
          <summary className="cursor-pointer">{p.faltan_en_diccionario.length} tablas tuyas que ningún procedimiento del MIS usa</summary>
          <ul className="mt-2 columns-1 gap-6 font-mono sm:columns-2">{p.faltan_en_diccionario.map((n) => <li key={n}>{n}</li>)}</ul>
        </details>
      )}
    </div>
  );
}

/** Cuándo se generó el diccionario; si todavía no hay, cómo generarlo. */
function Datos({ d }: { d: DicDatos }) {
  if (!d.generado) {
    return (
      <Aviso tono="info">
        <span>Todavía no hay detalle de tablas ni columnas: solo se ve el catálogo de reportes. <Link href="/diccionario/procesos/construir" className="font-medium underline">Genéralo desde la base</Link>.</span>
      </Aviso>
    );
  }
  return <p className="text-xs text-muted-foreground">Tablas y columnas generadas desde la base, <Hace iso={d.generado} />.</p>;
}

/** De dónde sale el catálogo de reportes y en qué se aparta del diccionario guardado (lo nuevo en la base y lo que ya no está). */
function Catalogo({ c }: { c: DicOrigenCatalogo }) {
  const lista = (codigos: string[]) => `${codigos.slice(0, 8).join(", ")}${codigos.length > 8 ? ` y ${codigos.length - 8} más` : ""}`;
  return (
    <div className="flex flex-col gap-2">
      {c.motivo
        ? <Aviso>No pude leer <span className="font-mono">mod_rep.rep.RREGREP01</span>: {c.motivo}. Se muestra el catálogo del diccionario guardado.</Aviso>
        : <p className="text-xs text-muted-foreground">Catálogo leído en vivo de <span className="font-mono">{c.fuente}</span>.</p>}
      {c.nuevos.length > 0 && <Aviso tono="info">{c.nuevos.length} reportes están en la base y aún no en el diccionario ({lista(c.nuevos)}): genera el diccionario de nuevo para incluirlos.</Aviso>}
      {c.retirados.length > 0 && <Aviso>{c.retirados.length} reportes del diccionario ya no están en la base ({lista(c.retirados)}).</Aviso>}
    </div>
  );
}

/** Resumen del diccionario hecho de gráficos: avance por base, calidad y lo que aporta a tus reportes. */
export function PanelResumen() {
  const { datos: r, error, recargar } = useConsulta("dic/resumen", api.dic.resumen);
  const potencial = useConsulta("dic/potencial", api.dic.potencial);
  const hallazgos = useConsulta("dic/hallazgos", () => api.dic.hallazgos());
  return (
    <Pagina>
      <Marco icono={<BookOpen />} titulo="Diccionario"
        descripcion={r ? `${r.reportes} reportes · ${r.procedimientos} procedimientos · ${r.tablas} tablas · ${r.columnas.toLocaleString("es-PE")} columnas del MIS` : "Qué procedimiento ejecuta cada reporte del MIS, qué tablas usa y qué columnas."}>
        {error ? <ErrorEnLinea titulo="No se pudo cargar el diccionario" detalle={error} onReintentar={recargar} /> : !r ? <EsqueletoFilas filas={2} alto="h-40" /> : (
          <>
            <Datos d={r.datos} />
            <Catalogo c={r.catalogo} />
            <div className="grid gap-4 lg:grid-cols-2">
            <Tarjeta titulo="Avance de la documentación" descripcion={`${r.validados} de ${r.procedimientos} procedimientos validados`}>
              <Avance bases={r.bases} />
            </Tarjeta>
            <Tarjeta titulo="Calidad" descripcion={<>{r.errores} errores y {r.avisos} avisos</>}>
              {hallazgos.error ? <ErrorEnLinea titulo="No se pudo cargar la calidad" detalle={hallazgos.error} onReintentar={hallazgos.recargar} />
                : hallazgos.datos ? <Calidad hallazgos={hallazgos.datos} /> : <EsqueletoFilas filas={3} />}
            </Tarjeta>
            </div>
          </>
        )}
      </Marco>
      {r && (
        <Tarjeta titulo="Lo que aporta a tus reportes" descripcion="El diccionario cruzado con las tablas que usan tus reportes.">
          {potencial.error ? <ErrorEnLinea titulo="No se pudo cruzar con tus reportes" detalle={potencial.error} onReintentar={potencial.recargar} /> : !potencial.datos ? <EsqueletoFilas filas={3} /> : (
            <>
              <Cobertura p={potencial.datos} />
              {potencial.datos.fechas.length > 0 && (
                <Table>
                  <TableHeader><TableRow><TableHead>Fecha por confirmar en</TableHead><TableHead>Hoy</TableHead><TableHead>Candidatas del diccionario</TableHead></TableRow></TableHeader>
                  <TableBody>
                    {potencial.datos.fechas.map((s) => (
                      <TableRow key={s.tabla}>
                        <TableCell><EnlaceTabla nombre={s.tabla} /></TableCell>
                        <TableCell className="font-mono text-[12px]">{s.actual ?? "—"}</TableCell>
                        <TableCell className="font-mono text-[12px]">{s.candidatas.join(", ")}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              )}
              <div className="flex flex-col gap-2">
                <h3 className="text-sm font-semibold">Tablas que el MIS más usa y tus reportes no</h3>
                <p className="text-xs text-muted-foreground">Buenas candidatas para tus próximos reportes. Pulsa una barra para ver sus columnas y fechas.</p>
                <Candidatas p={potencial.datos} />
              </div>
            </>
          )}
        </Tarjeta>
      )}
    </Pagina>
  );
}
