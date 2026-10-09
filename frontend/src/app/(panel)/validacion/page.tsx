import { Suspense } from "react";
import { PanelValidacionMasiva } from "@/features/validacion/panel-validacion";

export default function PaginaValidacion() {
  return (
    <Suspense>
      <PanelValidacionMasiva />
    </Suspense>
  );
}
