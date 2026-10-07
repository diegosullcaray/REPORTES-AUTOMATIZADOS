import { FileSpreadsheet } from "lucide-react";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { TablaReportes } from "@/features/reportes/tabla-reportes";

/** Escritorio: catálogo completo. En el celular esta ruta muestra solo la lista del sidebar de reportes. */
export default function PaginaReportes() {
  return (
    <div className="hidden md:block">
      <Pagina>
        <Marco icono={<FileSpreadsheet />} titulo="Reportes" descripcion="Los reportes del legado, con su responsable y el resultado de su última ejecución.">
          <TablaReportes />
        </Marco>
      </Pagina>
    </div>
  );
}
