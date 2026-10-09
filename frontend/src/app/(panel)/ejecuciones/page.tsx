import { History } from "lucide-react";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { TablaEjecuciones } from "@/features/ejecuciones/tabla-ejecuciones";

export default function PaginaEjecuciones() {
  return (
    <Pagina>
      <Marco icono={<History />} titulo="Ejecuciones" descripcion="Todas las ejecuciones de reportes en un solo lugar; se actualiza sola mientras hay algo en curso.">
        <TablaEjecuciones />
      </Marco>
    </Pagina>
  );
}
