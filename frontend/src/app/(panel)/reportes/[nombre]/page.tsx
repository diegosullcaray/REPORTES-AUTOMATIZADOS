import { Suspense } from "react";
import { DetalleReporte } from "@/features/reportes/detalle-reporte";

export default async function PaginaReporte({ params }: PageProps<"/reportes/[nombre]">) {
  const { nombre } = await params;
  return (
    <Suspense>
      <DetalleReporte nombre={decodeURIComponent(nombre)} />
    </Suspense>
  );
}
