"use client";

import { PlugZap } from "lucide-react";
import { useState } from "react";
import { Chip, EsqueletoFilas, EstadoVacio, ErrorEnLinea } from "@/components/estados";
import { Button } from "@/components/ui/button";
import { Ventana } from "@/components/ventana";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";

const SERVIDORES: Record<string, string> = {
  mish: "MISHWBDDES01 · Windows · storage, appj",
  slc: "172.24.2.213 · Windows · dwh, dma, csd, intcom, slc",
  rcc: "172.20.0.70 · SQL · dbriesgos, DBRCC, DW_Raw_v2…",
};

/** Prueba los 3 servidores bajo demanda (cada prueba abre conexiones reales, por eso no es automática). */
export function PanelConexiones() {
  const [vuelta, setVuelta] = useState(0);
  const { datos, error, cargando, recargar } = useConsulta(vuelta ? `conexiones/${vuelta}` : null, api.conexiones);

  return (
    <Ventana titulo="Conexiones" acciones={<Button size="sm" onClick={() => (vuelta ? recargar() : setVuelta(1))} disabled={cargando && vuelta > 0}>Probar conexiones</Button>}>
      {!vuelta ? (
        <EstadoVacio icono={PlugZap} titulo="Prueba los 3 servidores" descripcion="Comprueba VPN, driver ODBC y credenciales del .env antes del cierre de mes." />
      ) : error ? (
        <ErrorEnLinea titulo="No se pudo probar" detalle={error} onReintentar={recargar} />
      ) : cargando ? (
        <EsqueletoFilas filas={3} alto="h-14" />
      ) : datos && (
        <ul className="grid gap-3 sm:grid-cols-3">
          {Object.entries(datos).map(([nombre, estado]) => (
            <li key={nombre} className="mis-baldosa flex flex-col gap-1 p-3">
              <div className="flex items-center justify-between"><span className="font-semibold">{nombre}</span><Chip tono={estado === "OK" ? "exito" : "peligro"}>{estado === "OK" ? "OK" : "Falla"}</Chip></div>
              <span className="text-[12px] text-[var(--mis-text-secondary)]">{SERVIDORES[nombre] ?? ""}</span>
              {estado !== "OK" && <span className="text-[12px] text-[var(--mis-danger)]">{estado}</span>}
            </li>
          ))}
        </ul>
      )}
    </Ventana>
  );
}
