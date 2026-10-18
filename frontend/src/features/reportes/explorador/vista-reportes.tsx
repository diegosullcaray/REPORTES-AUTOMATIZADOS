"use client";

import { FileSpreadsheet } from "lucide-react";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { useSearchParams } from "next/navigation";
import { useConsulta } from "@/hooks/use-consulta";
import { useGrupos } from "@/hooks/use-grupos";
import { api } from "@/lib/api";
import { ExploradorReportes } from "./explorador-reportes";
import { NuevoGrupo } from "./nuevo-grupo";
import { NuevoReporte } from "./nuevo-reporte";

/** /reportes: en el tablero el botón crea un grupo; dentro de un grupo, un reporte (en el encabezado del marco, como «Create Project» de Dokploy). */
export function VistaReportes() {
  const reportes = useConsulta("reportes", api.reportes);
  const grupos = useGrupos();
  const grupo = useSearchParams().get("grupo");
  const actual = grupos.datos?.find((g) => g.id === grupo);
  return (
    <Pagina>
      <Marco icono={<FileSpreadsheet />} titulo="Reportes" descripcion="Entra por grupo y carpeta hasta el reporte."
        acciones={grupos.datos && (actual ? <NuevoReporte grupo={actual.id} nombreGrupo={actual.nombre} frecuenciaLibre={actual.propio} /> : !grupo && <NuevoGrupo />)}>
        <ExploradorReportes reportes={reportes} grupos={grupos} />
      </Marco>
    </Pagina>
  );
}
