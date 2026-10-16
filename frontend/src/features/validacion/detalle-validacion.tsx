"use client";

import { ShieldCheck } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";
import { ErrorEnLinea } from "@/components/estados";
import { useCorte } from "@/components/fecha-cierre";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import type { VerificacionGrupo } from "@/lib/tipos";
import { HistorialValidacion } from "./historial-validacion";
import { MensajeValidacion } from "./mensaje-validacion";
import { GRUPOS, type Grupo } from "./grupos";
import { PanelVerificacion } from "./panel-validacion";

const PESTANAS = ["validacion", "historial", "mensaje"] as const;
type Pestana = (typeof PESTANAS)[number];

/** Un responsable (Piero / Erick): verificar sus tablas, historial de verificaciones y el mensaje para pedir que las actualicen. */
export function DetalleValidacion({ grupo }: { grupo: Grupo }) {
  const reportes = useConsulta("reportes", api.reportes);
  const config = useConsulta("configuracion", api.configuracion);
  const historial = useConsulta(`validacion/${grupo}/historial`, () => api.historialValidacion(grupo));
  const [resultado, setResultado] = useState<VerificacionGrupo | null>(null); // vive aquí para no perderse al cambiar de pestaña
  const corte = useCorte("mensual", config.datos?.corte_mensual.fecha); // se elige en la cabecera (Fecha de cierre)
  const params = useSearchParams();
  const router = useRouter();
  const ruta = usePathname();
  const pedida = params.get("tab") as Pestana | null;
  const pestana: Pestana = pedida && PESTANAS.includes(pedida) ? pedida : "validacion";
  const irA = (p: Pestana) => router.replace(p === "validacion" ? ruta : `${ruta}?tab=${p}`, { scroll: false });

  return (
    <Pagina>
      <Marco icono={<ShieldCheck />} titulo={`Validación · ${GRUPOS[grupo]}`}
        descripcion="¿Llegaron las tablas al corte? Se verifican las de todos sus reportes mensuales, sin ejecutar nada (solo lectura).">
        {reportes.error ? <ErrorEnLinea titulo="No se pudo cargar el catálogo" detalle={reportes.error} onReintentar={reportes.recargar} /> : (
          <Tabs value={pestana} onValueChange={(v) => irA(v as Pestana)}>
            <TabsList className="w-full justify-start overflow-x-auto no-scrollbar sm:w-fit">
              <TabsTrigger value="validacion">Validación</TabsTrigger>
              <TabsTrigger value="historial">Historial</TabsTrigger>
              <TabsTrigger value="mensaje">Mensaje</TabsTrigger>
            </TabsList>
            <TabsContent value="validacion" className="pt-4">
              <PanelVerificacion grupo={grupo} corte={corte} reportes={reportes.datos ?? []} resultado={resultado} onResultado={setResultado} onVerificado={historial.recargar} />
            </TabsContent>
            <TabsContent value="historial" className="pt-4"><HistorialValidacion historial={historial} /></TabsContent>
            <TabsContent value="mensaje" className="pt-4"><MensajeValidacion grupo={grupo} historial={historial} /></TabsContent>
          </Tabs>
        )}
      </Marco>
    </Pagina>
  );
}
