import Link from "next/link";
import type { ReactNode } from "react";
import { Chip } from "@/components/estados";
import type { Tono } from "@/lib/formato";

/** Estado de un procedimiento del diccionario → color. */
export const TONO_SP: Record<string, Tono> = { validado: "exito", extraido: "info", pendiente: "aviso", "sin procedimiento": "peligro" };

export const EstadoSP = ({ estado }: { estado: string }) => <Chip tono={TONO_SP[estado] ?? "neutro"}>{estado}</Chip>;

export const enlaceTabla = (nombre: string) => `/diccionario/tablas/${encodeURIComponent(nombre)}`;
export const enlaceReporte = (codigo: string) => `/diccionario/reportes/${encodeURIComponent(codigo)}`;

export function EnlaceTabla({ nombre, children }: { nombre: string; children?: ReactNode }) {
  return <Link href={enlaceTabla(nombre)} className="font-mono text-[13px] hover:underline">{children ?? nombre}</Link>;
}

/** Indicador grande: número y rótulo (como las métricas del inicio). */
export function Indicador({ valor, texto, nota, tono }: { valor: ReactNode; texto: string; nota?: string; tono?: Tono }) {
  return (
    <div className="flex flex-col gap-0.5 rounded-xl border bg-background p-4">
      <span className={`text-2xl font-semibold tabular-nums ${tono === "peligro" ? "text-[var(--mis-danger)]" : ""}`}>{valor}</span>
      <span className="text-sm">{texto}</span>
      {nota && <span className="text-xs text-muted-foreground">{nota}</span>}
    </div>
  );
}
