"use client";

import { ArrowLeft, Table2 } from "lucide-react";
import Link from "next/link";
import { Aviso, Chip, ErrorEnLinea, EsqueletoFilas } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Tarjeta } from "@/components/tarjeta";
import { buttonVariants } from "@/components/ui/button";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { enlaceReporte } from "./comun";

/** Una tabla al detalle: sus columnas, qué reportes del MIS la leen y cómo la registran los reportes propios. */
export function DetalleTablaDic({ nombre }: { nombre: string }) {
  const { datos: t, error, recargar } = useConsulta(`dic/tabla/${nombre}`, () => api.dic.tabla(nombre));
  const reg = t?.registro;
  return (
    <Pagina>
      <Marco icono={<Table2 />} titulo={<span className="font-mono">{t?.nombre ?? nombre}</span>} descripcion={t?.descripcion ?? (t ? `Base ${t.base}${t.tipo ? ` · ${t.tipo}` : ""}. Sin descripción funcional: no se inventa.` : undefined)}
        acciones={<>{t && <Chip tono={t.existe === false ? "peligro" : t.existe ? "exito" : "neutro"}>{t.existe === null ? "sin comprobar" : t.existe ? "existe" : "no existe en la base"}</Chip>}<Link href={t ? `/diccionario/reportes?base=${encodeURIComponent(t.base)}&seccion=tablas` : "/diccionario/reportes"} className={buttonVariants({ variant: "ghost", size: "sm" })}><ArrowLeft /> {t ? t.base : "Bases"}</Link></>}>
        {error ? <ErrorEnLinea titulo="No se pudo cargar la tabla" detalle={error} onReintentar={recargar} /> : !t ? <EsqueletoFilas filas={5} /> : (
          <>
            <Tarjeta titulo="En tus reportes" descripcion="Cómo la tienen registrada los reportes de esta app (dominio/tablas.py).">
              {reg ? (
                <div className="flex flex-col gap-2 text-sm">
                  <span>Tipo <Chip>{reg.tipo}</Chip> · columna de fecha <span className="font-mono">{reg.col_fecha ?? "—"}</span> <Chip tono={reg.confianza === "confirmada" ? "exito" : "aviso"}>{reg.confianza}</Chip></span>
                  <span className="text-muted-foreground">La usan: {reg.reportes.join(", ") || "ningún reporte todavía"}</span>
                  {reg.confianza !== "confirmada" && t.columnas_detalle.some((c) => c.es_fecha) && (
                    <Aviso>Fecha por confirmar. Candidatas según los procedimientos: <span className="font-mono">{t.columnas_detalle.filter((c) => c.es_fecha).map((c) => c.nombre).join(", ")}</span></Aviso>
                  )}
                </div>
              ) : <p className="text-sm text-muted-foreground">Ningún reporte de esta app la usa todavía. Si quieres usarla, las columnas con fecha están marcadas abajo.</p>}
            </Tarjeta>
            <Tarjeta titulo="Columnas" descripcion={`${t.columnas} columna(s) usadas por ${t.procedimientos} procedimiento(s). Las de fecha están resaltadas.`}>
              <Table>
                <TableHeader><TableRow><TableHead>Columna</TableHead><TableHead>Tipo</TableHead><TableHead>Nulos</TableHead><TableHead>Confianza</TableHead><TableHead>La usan</TableHead></TableRow></TableHeader>
                <TableBody>
                  {t.columnas_detalle.map((c) => (
                    <TableRow key={c.nombre}>
                      <TableCell className="font-mono">{c.nombre} {c.es_fecha && <Chip tono="info">fecha</Chip>}</TableCell>
                      <TableCell>{c.tipo ?? "—"}</TableCell>
                      <TableCell>{c.acepta_nulos === null ? "—" : c.acepta_nulos ? "sí" : "no"}</TableCell>
                      <TableCell>{c.confianza ?? "—"}</TableCell>
                      <TableCell className="text-muted-foreground">{c.procedimientos.length} SP</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </Tarjeta>
            <Tarjeta titulo="Reportes del MIS que la leen">
              {t.reportes_mis.length ? <div className="flex flex-wrap gap-1.5">{t.reportes_mis.map((c) => <Link key={c} href={enlaceReporte(c)} className="rounded-md border px-1.5 py-0.5 font-mono text-[12px] hover:underline">{c}</Link>)}</div>
                : <p className="text-sm text-muted-foreground">Ninguno.</p>}
            </Tarjeta>
          </>
        )}
      </Marco>
    </Pagina>
  );
}
