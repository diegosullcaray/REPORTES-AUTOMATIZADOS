import { FileSpreadsheet } from "lucide-react";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { TablaReportes } from "@/features/reportes/tabla-reportes";

export default function PaginaReportes() {
  return (
    <Pagina>
      <Marco icono={<FileSpreadsheet />} titulo="Reportes" descripcion="Los reportes del legado, con su responsable y el resultado de su última ejecución.">
        <TablaReportes />
      </Marco>
    </Pagina>
  );
}
