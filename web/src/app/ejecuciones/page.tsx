import { Ventana } from "@/components/ventana";
import { TablaEjecuciones } from "@/features/ejecuciones/tabla-ejecuciones";

export default function PaginaEjecuciones() {
  return (
    <Ventana titulo="Ejecuciones">
      <TablaEjecuciones />
    </Ventana>
  );
}
