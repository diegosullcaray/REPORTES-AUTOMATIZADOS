"use client";

import { ChevronRight, UserRound } from "lucide-react";
import { ErrorEnLinea, EsqueletoFilas, Punto } from "@/components/estados";
import { Hace } from "@/components/hace";
import { REJILLA_TARJETAS, Tarjeta } from "@/components/tarjeta-enlace";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { GRUPOS, type Grupo } from "./grupos";

/** Un responsable por tarjeta (como los grupos de /reportes); entra a su pantalla de validación. El punto resume su última verificación. */
export function TarjetasValidacion() {
  const reportes = useConsulta("reportes", api.reportes);
  const piero = useConsulta("validacion/piero/historial/1", () => api.historialValidacion("piero", 1));
  const erick = useConsulta("validacion/erick/historial/1", () => api.historialValidacion("erick", 1));
  const ultima = { piero: piero.datos?.[0], erick: erick.datos?.[0] };

  const error = reportes.error ?? piero.error ?? erick.error;
  if (error) return <ErrorEnLinea titulo="No se pudo cargar la validación" detalle={error} onReintentar={() => { reportes.recargar(); piero.recargar(); erick.recargar(); }} />;
  if (!reportes.datos || !piero.datos || !erick.datos) return <EsqueletoFilas filas={2} alto="h-28" />;

  return (
    <div className={REJILLA_TARJETAS}>
      {(Object.keys(GRUPOS) as Grupo[]).map((g) => {
        const n = reportes.datos!.filter((r) => r.frecuencia === "mensual" && r.grupo === g).length;
        const u = ultima[g];
        const pendientes = u?.reportes.reduce((t, x) => t + x.pendientes, 0) ?? 0;
        return (
          <Tarjeta key={g} href={`/validacion/${g}`} icono={UserRound} titulo={GRUPOS[g]}
            estado={<Punto tono={!u ? "neutro" : pendientes ? "aviso" : "exito"} etiqueta={!u ? "Sin validar" : pendientes ? `${pendientes} tabla(s) sin actualizar` : "Al día"} />}
            pie={<><span>{n} reportes · {u ? <Hace iso={u.ejecutada} /> : "sin validar"}</span><ChevronRight className="size-4" /></>} />
        );
      })}
    </div>
  );
}
