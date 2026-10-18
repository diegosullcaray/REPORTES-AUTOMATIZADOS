import { Suspense } from "react";
import { VistaReportes } from "@/features/reportes/explorador/vista-reportes";

export default function PaginaReportes() {
  return (
    <Suspense>
      <VistaReportes />
    </Suspense>
  );
}
