import { Suspense } from "react";
import { PanelConfiguracion } from "@/features/configuracion/panel-configuracion";

export default function PaginaConfiguracion() {
  return (
    <Suspense>
      <PanelConfiguracion />
    </Suspense>
  );
}
