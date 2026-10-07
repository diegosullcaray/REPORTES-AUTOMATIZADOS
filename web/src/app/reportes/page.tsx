import { FileSpreadsheet } from "lucide-react";
import { EstadoVacio } from "@/components/estados";
import { Ventana } from "@/components/ventana";

/** En escritorio, mientras no se elige un reporte. En el celular esta ruta muestra solo la lista del sidebar. */
export default function PaginaReportes() {
  return (
    <div className="hidden md:block">
      <Ventana titulo="Reportes">
        <EstadoVacio icono={FileSpreadsheet} titulo="Elige un reporte"
          descripcion="Selecciónalo en el panel de la izquierda para validar sus tablas, ejecutarlo y revisar sus archivos." />
      </Ventana>
    </div>
  );
}
