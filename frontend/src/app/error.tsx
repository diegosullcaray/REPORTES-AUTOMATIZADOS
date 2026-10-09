"use client";

import { useEffect } from "react";
import { PaginaError } from "@/components/pagina-error";

/** Error inesperado de una pantalla fuera del panel (p. ej. el login). `retry` es la convención de esta versión de Next. */
export default function Error({ error, retry }: { error: Error & { digest?: string }; retry: () => void }) {
  useEffect(() => console.error(error), [error]);
  return <PaginaError codigo={500} mensaje="Vaya, algo salió mal." detalle={error.digest && `Referencia: ${error.digest}`} onReintentar={retry} />;
}
