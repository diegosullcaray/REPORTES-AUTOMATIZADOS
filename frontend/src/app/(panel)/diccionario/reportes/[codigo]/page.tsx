import { Suspense } from "react";
import { DetalleReporteDic } from "@/features/diccionario/detalle-reporte";

export default async function PaginaReporteDic({ params }: PageProps<"/diccionario/reportes/[codigo]">) {
  const { codigo } = await params;
  return (
    <Suspense>
      <DetalleReporteDic codigo={decodeURIComponent(codigo)} />
    </Suspense>
  );
}
