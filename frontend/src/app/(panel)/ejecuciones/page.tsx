import { History } from "lucide-react";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { TablaEjecuciones } from "@/features/ejecuciones/tabla-ejecuciones";

export default function PaginaEjecuciones() {
  return (
    <Pagina>
      <Marco icono={<History />} titulo="Ejecuciones" descripcion="Agrupadas por reporte y fecha de corte: abre un proceso para ver sus pasos. Se actualiza sola.">
        <TablaEjecuciones />
      </Marco>
    </Pagina>
  );
}
