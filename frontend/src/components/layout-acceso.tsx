import { FileSpreadsheet } from "lucide-react";
import type { ReactNode } from "react";
import { ModoTema } from "@/components/modo-tema";
import { Card, CardContent } from "@/components/ui/card";
import { FieldDescription } from "@/components/ui/field";

/** Marco de las pantallas de acceso (bloque login-04 de shadcn): tarjeta de dos columnas, formulario a un lado y panel de marca al otro. */
export function LayoutAcceso({ children, lema }: { children: ReactNode; lema?: ReactNode }) {
  return (
    <div className="relative flex min-h-svh flex-col items-center justify-center bg-secondary p-6 md:p-10">
      <ModoTema className="absolute top-4 right-4" />
      <div className="w-full max-w-sm md:max-w-4xl">
        <Card className="overflow-hidden p-0 shadow-[var(--mis-shadow-lg)]">
          <CardContent className="grid p-0 md:grid-cols-2">
            <div className="p-6 md:p-8">{children}</div>
            <div className="relative hidden flex-col bg-sidebar p-10 text-sidebar-foreground md:flex">
              <span className="flex items-center gap-3 text-lg font-medium">
                <span className="flex size-10 items-center justify-center rounded-xl border border-sidebar-border bg-sidebar-accent"><FileSpreadsheet className="size-5" /></span>
                Reportes automatizados
              </span>
            </div>
          </CardContent>
        </Card>
        <FieldDescription className="px-6 pt-6 text-center">{lema ?? "Validación, ejecución y entrega de los reportes de Financiera Confianza."}</FieldDescription>
      </div>
    </div>
  );
}
