// Estados de MIS (shared/ui: app-inline-error, app-empty-state, app-list-skeleton). Orden: error · cargando · vacío · contenido.
import { AlertCircle, Inbox, type LucideIcon } from "lucide-react";
import type { ReactNode } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import type { Tono } from "@/lib/formato";

export function ErrorEnLinea({ titulo, detalle, onReintentar }: { titulo: string; detalle?: string | null; onReintentar?: () => void }) {
  return (
    <div role="alert" className="flex items-start gap-3 rounded-[10px] border p-3"
      style={{ background: "var(--mis-danger-light)", borderColor: "color-mix(in srgb, var(--mis-danger) 25%, transparent)" }}>
      <AlertCircle className="mt-px size-4 shrink-0 text-[var(--mis-danger)]" />
      <div className="flex flex-1 flex-col gap-0.5">
        <span className="text-[13px] font-medium text-[var(--mis-danger)]">{titulo}</span>
        {detalle && <span className="text-[12px] whitespace-pre-line text-[var(--mis-text-secondary)]">{detalle}</span>}
      </div>
      {onReintentar && (
        <button onClick={onReintentar}
          className="rounded-[6px] border border-[var(--mis-danger)] px-2 py-0.5 text-xs whitespace-nowrap text-[var(--mis-danger)] transition-colors duration-150 hover:bg-[var(--mis-hover-bg)]">
          Reintentar
        </button>
      )}
    </div>
  );
}

export function EstadoVacio({ titulo, descripcion, icono: Icono = Inbox, accion }: { titulo: string; descripcion?: string; icono?: LucideIcon; accion?: ReactNode }) {
  return (
    <div className="flex flex-col items-center justify-center gap-3 px-6 py-12 text-center">
      <div className="flex size-16 items-center justify-center rounded-full bg-[var(--mis-primary-light)]">
        <Icono className="size-7 text-[var(--mis-primary-text)] opacity-50" />
      </div>
      <h4 className="m-0 text-[17px] font-semibold text-[var(--mis-text-primary)]">{titulo}</h4>
      {descripcion && <p className="m-0 max-w-[340px] text-[13px] leading-normal text-[var(--mis-text-secondary)]">{descripcion}</p>}
      {accion}
    </div>
  );
}

/** Esqueleto de la propia tabla/lista mientras llega su carga real. */
export function EsqueletoFilas({ filas = 6, alto = "h-10" }: { filas?: number; alto?: string }) {
  return (
    <div className="flex flex-col gap-2" aria-busy="true" aria-label="Cargando">
      {Array.from({ length: filas }, (_, i) => <Skeleton key={i} className={`${alto} w-full rounded-[var(--mis-radius-sm)]`} />)}
    </div>
  );
}

const TONOS: Record<Tono, [string, string]> = {
  exito: ["var(--mis-success-light)", "var(--mis-success)"],
  aviso: ["var(--mis-warning-light)", "var(--mis-warning)"],
  peligro: ["var(--mis-danger-light)", "var(--mis-danger)"],
  info: ["var(--mis-secondary-light)", "var(--mis-primary-text)"],
  neutro: ["var(--mis-primary-light)", "var(--mis-text-secondary)"],
};

export function Chip({ tono = "neutro", children }: { tono?: Tono; children: ReactNode }) {
  const [fondo, texto] = TONOS[tono];
  return (
    <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[11px] font-medium whitespace-nowrap"
      style={{ background: fondo, color: texto }}>
      {children}
    </span>
  );
}

/** Aviso destacado (no es error): reglas del reporte, escritura en BD, forzar… */
export function Aviso({ tono = "aviso", children }: { tono?: Tono; children: ReactNode }) {
  const [fondo, texto] = TONOS[tono];
  return (
    <div className="rounded-[10px] border p-3 text-[13px]" style={{ background: fondo, borderColor: `color-mix(in srgb, ${texto} 30%, transparent)` }}>
      <div style={{ color: texto }}>{children}</div>
    </div>
  );
}
