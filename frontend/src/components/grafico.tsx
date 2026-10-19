"use client";

import { BarChart } from "echarts/charts";
import { GridComponent, LegendComponent, TooltipComponent } from "echarts/components";
import * as echarts from "echarts/core";
import { SVGRenderer } from "echarts/renderers";
import { useTheme } from "next-themes";
import { useEffect, useRef, type ReactNode } from "react";

echarts.use([BarChart, GridComponent, LegendComponent, TooltipComponent, SVGRenderer]);

/** Colores del tema (tokens `--mis-*` ya resueltos): se vuelven a leer al cambiar claro/oscuro. */
export interface Colores {
  /** Resuelve una expresión CSS (`var(--mis-x)`, `color-mix(…)`) al color que pinta el navegador. */
  c: (css: string) => string;
  texto: string;
  tenue: string;
  linea: string;
  superficie: string;
  marca: string;
  exito: string;
  aviso: string;
  peligro: string;
}

function leerColores(): Colores {
  const sonda = document.createElement("span");
  document.body.appendChild(sonda);
  const c = (css: string) => {
    sonda.style.color = "";
    sonda.style.color = css;
    return getComputedStyle(sonda).color;
  };
  const colores: Colores = {
    c, texto: c("var(--mis-text-primary)"), tenue: c("var(--mis-text-secondary)"), linea: c("var(--mis-border)"), superficie: c("var(--mis-surface)"),
    marca: c("var(--mis-primary)"), exito: c("var(--mis-success)"), aviso: c("var(--mis-warning)"), peligro: c("var(--mis-danger)"),
  };
  sonda.remove();
  return colores;
}

/**
 * Gráfico de ECharts con los colores del tema. `opcion` recibe los colores y devuelve la configuración.
 * `resumen` es lo que lee un lector de pantalla; `tabla` deja ver los mismos datos sin depender del color.
 */
export function Grafico({ opcion, alto, resumen, tabla, alClic }: {
  opcion: (c: Colores) => echarts.EChartsCoreOption;
  alto: number;
  resumen: string;
  tabla?: { columnas: string[]; filas: (string | number)[][] };
  alClic?: (nombre: string) => void;
}) {
  const caja = useRef<HTMLDivElement>(null);
  const grafico = useRef<echarts.ECharts | null>(null);
  const { resolvedTheme } = useTheme();
  const clicRef = useRef(alClic);
  useEffect(() => {
    clicRef.current = alClic;
  });

  useEffect(() => {
    if (!caja.current) return;
    const g = echarts.init(caja.current, undefined, { renderer: "svg" });
    g.on("click", (e) => clicRef.current?.(String(e.name)));
    const ajuste = new ResizeObserver(() => g.resize());
    ajuste.observe(caja.current);
    grafico.current = g;
    return () => {
      ajuste.disconnect();
      g.dispose();
      grafico.current = null;
    };
  }, []);

  // Se repinta al cambiar los datos o el tema; `true` = reemplaza la configuración anterior en vez de mezclarla.
  useEffect(() => {
    grafico.current?.setOption({ textStyle: { fontFamily: "inherit" }, ...opcion(leerColores()) }, true);
  }, [opcion, resolvedTheme]);

  return (
    <div className="flex flex-col gap-2">
      <div ref={caja} role="img" aria-label={resumen} style={{ height: alto, cursor: alClic ? "pointer" : undefined }} />
      {tabla && <TablaDeDatos {...tabla} />}
    </div>
  );
}

function TablaDeDatos({ columnas, filas }: { columnas: string[]; filas: (string | number)[][] }): ReactNode {
  return (
    <details className="text-xs text-muted-foreground">
      <summary className="cursor-pointer">Ver como tabla</summary>
      <table className="mt-2 w-full">
        <thead><tr>{columnas.map((c, i) => <th key={c} className={`py-1 font-medium ${i ? "text-right" : "text-left"}`}>{c}</th>)}</tr></thead>
        <tbody>{filas.map((f, i) => <tr key={i} className="border-t">{f.map((v, j) => <td key={j} className={`py-1 ${j ? "text-right tabular-nums" : ""}`}>{v}</td>)}</tr>)}</tbody>
      </table>
    </details>
  );
}
