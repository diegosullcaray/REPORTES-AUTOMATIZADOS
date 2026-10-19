import { Suspense } from "react";
import { PanelProcesos } from "@/features/diccionario/procesos";

export default function PaginaProcesosDic() {
  return (
    <Suspense>
      <PanelProcesos />
    </Suspense>
  );
}
