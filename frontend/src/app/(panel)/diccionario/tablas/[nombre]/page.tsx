import { Suspense } from "react";
import { DetalleTablaDic } from "@/features/diccionario/detalle-tabla";

export default async function PaginaTablaDic({ params }: PageProps<"/diccionario/tablas/[nombre]">) {
  const { nombre } = await params;
  return (
    <Suspense>
      <DetalleTablaDic nombre={decodeURIComponent(nombre)} />
    </Suspense>
  );
}
