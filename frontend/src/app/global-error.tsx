"use client";

import { PaginaError } from "@/components/pagina-error";
import "./globals.css";

/** Último recurso: falla el propio layout raíz. Reemplaza `<html>`, así que no hay proveedores de tema. */
export default function ErrorGlobal({ retry }: { error: Error & { digest?: string }; retry: () => void }) {
  return (
    <html lang="es">
      <body>
        <PaginaError codigo={500} mensaje="Vaya, la aplicación no pudo cargarse." onReintentar={retry} />
      </body>
    </html>
  );
}
