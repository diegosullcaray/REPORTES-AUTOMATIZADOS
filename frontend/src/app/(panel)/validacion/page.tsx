import { ShieldCheck } from "lucide-react";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { TarjetasValidacion } from "@/features/validacion/tarjetas-validacion";

export default function PaginaValidacion() {
  return (
    <Pagina>
      <Marco icono={<ShieldCheck />} titulo="Validación de tablas" descripcion="Elige un responsable para verificar sus tablas.">
        <TarjetasValidacion />
      </Marco>
    </Pagina>
  );
}
