import { ShieldCheck } from "lucide-react";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { TablaValidacion } from "@/features/validacion/tabla-validacion";

export default function PaginaValidacion() {
  return (
    <Pagina>
      <Marco icono={<ShieldCheck />} titulo="Validación de tablas" descripcion="Estado de los reportes mensuales de Piero y Erick en su última validación. Entra a un responsable para verificar sus tablas, ver su historial y pedir que las actualicen.">
        <TablaValidacion />
      </Marco>
    </Pagina>
  );
}
