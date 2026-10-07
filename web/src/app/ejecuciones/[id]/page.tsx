import { DetalleEjecucion } from "@/features/ejecuciones/detalle-ejecucion";

export default async function PaginaEjecucion({ params }: PageProps<"/ejecuciones/[id]">) {
  const { id } = await params;
  return <DetalleEjecucion id={id} />;
}
