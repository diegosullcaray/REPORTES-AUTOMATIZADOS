"use client";

import { FileSpreadsheet } from "lucide-react";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ExploradorReportes } from "./explorador-reportes";
import { NuevaSeccion } from "./nueva-seccion";

/** /reportes: el botón «Nueva sección» va en el encabezado del marco (como «Create Project» de Dokploy); el explorador comparte sus datos. */
export function VistaReportes() {
  const reportes = useConsulta("reportes", api.reportes);
  const secciones = useConsulta("secciones", api.secciones);
  return (
    <Pagina>
      <Marco icono={<FileSpreadsheet />} titulo="Reportes" descripcion="Entra por grupo y carpeta hasta el reporte."
        acciones={reportes.datos && <NuevaSeccion reportes={reportes.datos} onCreada={secciones.recargar} />}>
        <ExploradorReportes reportes={reportes} secciones={secciones} />
      </Marco>
    </Pagina>
  );
}
