import type { ReactNode } from "react";

/** Contenedor de una vista: ocupa todo el ancho y el alto del área de contenido. */
export function Pagina({ children }: { children: ReactNode }) {
  return <div className="flex w-full min-w-0 flex-1 flex-col gap-4 p-3 sm:p-4">{children}</div>;
}
