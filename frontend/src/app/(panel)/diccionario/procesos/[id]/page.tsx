import { Suspense } from "react";
import { DetalleProceso } from "@/features/diccionario/detalle-proceso";

export default async function PaginaProcesoDic({ params }: PageProps<"/diccionario/procesos/[id]">) {
  const { id } = await params;
  return (
    <Suspense>
      <DetalleProceso id={decodeURIComponent(id)} />
    </Suspense>
  );
}
