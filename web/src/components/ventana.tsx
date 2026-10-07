import type { ReactNode } from "react";

/** Ventana de módulo de MIS: barra con semáforo, título centrado y acciones a la derecha. */
export function Ventana({ titulo, acciones, children }: { titulo: string; acciones?: ReactNode; children: ReactNode }) {
  return (
    <section className="mis-window animate-in fade-in-0 duration-200 md:min-h-[calc(100vh-130px)]">
      <header className="mis-window-bar">
        <div className="flex items-center gap-2" aria-hidden>
          <span className="mis-window-light mis-window-light--cerrar" />
          <span className="mis-window-light mis-window-light--minimizar" />
          <span className="mis-window-light mis-window-light--zoom" />
        </div>
        <h1 className="truncate text-[13px] font-semibold text-[var(--mis-text-primary)]">{titulo}</h1>
        <div className="flex justify-end gap-1">{acciones}</div>
      </header>
      <div className="flex flex-col gap-4 p-3 sm:p-5">{children}</div>
    </section>
  );
}
