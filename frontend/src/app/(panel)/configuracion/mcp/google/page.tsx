import { Suspense } from "react";
import { PanelMcp } from "@/features/configuracion/panel-mcp";

export default function PaginaMcpGoogle() {
  // useSearchParams (vuelta de Google con ?code=) exige un límite de Suspense en una página estática.
  return <Suspense><PanelMcp /></Suspense>;
}
