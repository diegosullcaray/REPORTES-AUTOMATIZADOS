"use client";

import { useEffect } from "react";
import { PaginaError } from "@/components/pagina-error";

/** Error inesperado dentro del panel: el sidebar y el encabezado se conservan y solo falla el contenido. */
export default function ErrorDelPanel({ error, retry }: { error: Error & { digest?: string }; retry: () => void }) {
  useEffect(() => console.error(error), [error]);
  return <PaginaError compacta codigo={500} mensaje="Vaya, algo salió mal en esta pantalla." detalle={error.digest && `Referencia: ${error.digest}`} onReintentar={retry} />;
}
