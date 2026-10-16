import { notFound } from "next/navigation";
import { Suspense } from "react";
import { DetalleValidacion } from "@/features/validacion/detalle-validacion";
import { GRUPOS, type Grupo } from "@/features/validacion/grupos";

export default async function PaginaValidacionGrupo({ params }: PageProps<"/validacion/[grupo]">) {
  const { grupo } = await params;
  if (!(grupo in GRUPOS)) notFound();
  return (
    <Suspense>
      <DetalleValidacion grupo={grupo as Grupo} />
    </Suspense>
  );
}
