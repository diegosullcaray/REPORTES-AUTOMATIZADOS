import { Suspense } from "react";
import { ListaMcp } from "@/features/configuracion/lista-mcp";

export default function PaginaMcp() {
  // useSearchParams (reenvío de la vuelta de Google con ?code=) exige un límite de Suspense en una página estática.
  return <Suspense><ListaMcp /></Suspense>;
}
