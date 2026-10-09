import type { ReactNode } from "react";

/** Contenedor de una vista: ancho máximo y márgenes del área de contenido. */
export function Pagina({ children }: { children: ReactNode }) {
  return <div className="mx-auto flex w-full max-w-7xl flex-col gap-4 p-3 sm:p-4">{children}</div>;
}
