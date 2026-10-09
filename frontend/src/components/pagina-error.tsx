import { ChevronLeft, FileSpreadsheet, RotateCw } from "lucide-react";
import Link from "next/link";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface Props {
  /** Código grande (404, 500…). */
  codigo: number;
  mensaje: string;
  detalle?: string;
  /** Si se pasa, aparece «Reintentar». */
  onReintentar?: () => void;
  /** Dentro del panel (con sidebar): sin cabecera ni alto de pantalla completa. */
  compacta?: boolean;
}

/** Página de error al estilo de Dokploy: código grande, mensaje y salida al inicio. Los colores salen de los tokens. */
export function PaginaError({ codigo, mensaje, detalle, onReintentar, compacta }: Props) {
  return (
    <div className={cn("mx-auto flex w-full max-w-3xl flex-col", compacta ? "flex-1 justify-center py-10" : "min-h-svh")}>
      {!compacta && (
        <header className="mb-auto flex justify-center py-4">
          <Link href="/" className="flex items-center gap-2 text-sm font-medium">
            <span className="flex size-8 items-center justify-center rounded-lg border bg-muted"><FileSpreadsheet className="size-4" /></span>
            Reportes automatizados
          </Link>
        </header>
      )}
      <main className="px-4 py-10 text-center sm:px-6 lg:px-8">
        <h1 className="block text-7xl font-bold text-primary sm:text-9xl">{codigo}</h1>
        <p className="mt-3 text-muted-foreground">{mensaje}</p>
        {detalle && <p className="mt-2 font-mono text-xs break-all text-muted-foreground">{detalle}</p>}
        <div className="mt-5 flex flex-col items-center justify-center gap-2 sm:flex-row sm:gap-3">
          {onReintentar && (
            <button type="button" onClick={onReintentar} className={buttonVariants({ variant: "default", className: "gap-2" })}><RotateCw className="size-4" /> Reintentar</button>
          )}
          <Link href="/" className={buttonVariants({ variant: "secondary", className: "gap-2" })}><ChevronLeft className="size-4" /> Ir al inicio</Link>
        </div>
      </main>
      {!compacta && (
        <footer className="mt-auto py-5 text-center text-sm text-muted-foreground">
          {codigo >= 500 ? "Si el problema continúa, comprueba que la API de reportes esté corriendo." : "Revisa la dirección o vuelve al inicio."}
        </footer>
      )}
    </div>
  );
}
