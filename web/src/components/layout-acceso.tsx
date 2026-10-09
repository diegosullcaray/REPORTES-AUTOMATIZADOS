import { FileSpreadsheet } from "lucide-react";
import type { ReactNode } from "react";

/** Marco de las pantallas de acceso (como el OnboardingLayout de Dokploy): panel de marca a la izquierda, formulario centrado. */
export function LayoutAcceso({ children, lema }: { children: ReactNode; lema?: ReactNode }) {
  return (
    <div className="relative flex min-h-svh w-full flex-col items-center justify-center lg:grid lg:grid-cols-2">
      <div className="relative hidden h-full flex-col bg-muted p-10 lg:flex lg:border-r">
        <span className="flex items-center gap-3 text-lg font-medium">
          <span className="flex size-10 items-center justify-center rounded-xl border bg-background"><FileSpreadsheet className="size-5" /></span>
          Reportes automatizados
        </span>
        <p className="mt-auto text-lg">{lema ?? "Validación, ejecución y entrega de los reportes de Financiera Confianza."}</p>
      </div>
      <div className="mx-auto flex w-full max-w-lg flex-1 flex-col justify-center gap-6 px-4 py-8">{children}</div>
    </div>
  );
}
