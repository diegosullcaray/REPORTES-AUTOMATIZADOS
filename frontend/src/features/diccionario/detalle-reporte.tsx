"use client";

import { ArrowLeft, FileText } from "lucide-react";
import Link from "next/link";
import { Chip, ErrorEnLinea, EsqueletoFilas } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Tarjeta } from "@/components/tarjeta";
import { buttonVariants } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { EnlaceTabla, EstadoSP } from "./comun";

/** Un reporte del MIS al detalle: su procedimiento, parámetros, tablas con las columnas que usa, pantallas del front y hallazgos. */
export function DetalleReporteDic({ codigo }: { codigo: string }) {
  const { datos: r, error, recargar } = useConsulta(`dic/reporte/${codigo}`, () => api.dic.reporte(codigo));
  const sp = r?.procedimiento_detalle;
  return (
    <Pagina>
      <Marco icono={<FileText />} titulo={<span className="font-mono">{codigo}</span>} descripcion={r?.descripcion}
        acciones={<>{r && <EstadoSP estado={r.estado} />}<Link href={r ? `/diccionario/reportes?base=${encodeURIComponent(r.procedimiento.split(".")[0])}&seccion=procedimientos` : "/diccionario/reportes"} className={buttonVariants({ variant: "ghost", size: "sm" })}><ArrowLeft /> {r ? r.procedimiento.split(".")[0] : "Bases"}</Link></>}>
        {error ? <ErrorEnLinea titulo="No se pudo cargar el reporte" detalle={error} onReintentar={recargar} /> : !r ? <EsqueletoFilas filas={4} /> : (
          <>
            <Tarjeta titulo="Procedimiento" descripcion={sp ? <><span className="font-mono">{sp.nombre}</span> · base {sp.base}</> : "El catálogo lo nombra pero no se encontró en la base."}>
              {sp && (
                <>
                  <Table>
                    <TableHeader><TableRow><TableHead>Parámetro</TableHead><TableHead>Tipo</TableHead><TableHead>Por defecto</TableHead><TableHead>Salida</TableHead></TableRow></TableHeader>
                    <TableBody>
                      {sp.parametros.map((p) => (
                        <TableRow key={p.nombre}>
                          <TableCell className="font-mono">{p.nombre}</TableCell><TableCell>{p.tipo ?? "—"}</TableCell>
                          <TableCell>{p.por_defecto ?? "—"}</TableCell><TableCell>{p.salida ? "sí" : ""}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                  {sp.resultados.length > 0 && <p className="text-sm text-muted-foreground">Devuelve {sp.resultados.length} resultado(s): {sp.resultados.map((rs) => rs.join(", ")).join(" · ")}</p>}
                  {sp.invoca.length > 0 && <p className="text-sm text-muted-foreground">Invoca a: <span className="font-mono">{sp.invoca.join(", ")}</span></p>}
                </>
              )}
            </Tarjeta>
            {sp?.tablas.map((t) => (
              <Tarjeta key={t.nombre} titulo={<EnlaceTabla nombre={t.nombre} />} descripcion={`${t.usos.join(", ")} · ${t.columnas.length} columna(s) que usa este procedimiento`}>
                <div className="flex flex-wrap gap-1.5">
                  {t.columnas.map((c) => (
                    <span key={c.nombre} title={c.confianza ?? undefined} className="rounded-md border px-1.5 py-0.5 font-mono text-[12px]" style={c.es_fecha ? { borderColor: "var(--mis-primary-text)" } : undefined}>{c.nombre}</span>
                  ))}
                </div>
              </Tarjeta>
            ))}
            <Tarjeta titulo="Pantallas del front" descripcion="Dónde se ve este reporte en MIS-angular-front.">
              {r.front.length ? <ul className="list-disc pl-5 text-sm">{r.front.map((f) => <li key={f}>{f}</li>)}</ul> : <p className="text-sm text-muted-foreground">Ninguna pantalla lo pide.</p>}
            </Tarjeta>
            {r.hallazgos.length > 0 && (
              <Tarjeta titulo="Hallazgos" descripcion="Lo que la verificación encontró en este procedimiento o en este reporte.">
                <ul className="flex flex-col gap-2 text-sm">
                  {r.hallazgos.map((h, i) => (
                    <li key={i} className="flex flex-wrap items-center gap-2"><Chip tono={h.nivel === "error" ? "peligro" : "aviso"}>{h.nivel}</Chip><span>{h.regla}</span><span className="font-mono text-[12px] text-muted-foreground">{h.objeto}</span><span className="text-muted-foreground">{h.detalle}</span></li>
                  ))}
                </ul>
              </Tarjeta>
            )}
          </>
        )}
      </Marco>
    </Pagina>
  );
}
