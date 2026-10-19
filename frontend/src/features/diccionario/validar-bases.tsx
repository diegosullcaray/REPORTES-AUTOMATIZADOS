"use client";

import { PlugZap } from "lucide-react";
import { Chip, ErrorEnLinea } from "@/components/estados";
import { Tarjeta } from "@/components/tarjeta";
import { Button } from "@/components/ui/button";
import { useConsulta } from "@/hooks/use-consulta";
import { useProbarServidores } from "@/hooks/use-probar-servidores";
import { api } from "@/lib/api";

/** Valida que la API llega a los 3 servidores SQL (mish, slc, rcc): lo mismo que Bases de datos, aquí a mano para los procesos del diccionario. */
export function ValidarBases() {
  const { datos, error, recargar } = useConsulta("servidores", api.servidores);
  const { probando, resultados, probar } = useProbarServidores();
  if (error) return <ErrorEnLinea titulo="No se pudieron cargar los servidores" detalle={error} onReintentar={recargar} />;
  return (
    <Tarjeta titulo="Validar las bases de datos" descripcion="Comprueba que la API se conecta a cada servidor (SELECT 1). Las credenciales viven solo en el .env."
      acciones={<Button size="sm" disabled={probando.size > 0 || !datos} onClick={() => datos?.forEach(probar)}><PlugZap /> Validar todas</Button>}>
      <ul className="divide-y">
        {datos?.map((s) => {
          const r = resultados[s.nombre];
          return (
            <li key={s.nombre} className="flex flex-wrap items-center justify-between gap-2 py-2">
              <span className="flex flex-col"><span className="font-medium">{s.nombre}</span><span className="font-mono text-xs text-muted-foreground">{s.servidor}</span></span>
              <span className="flex items-center gap-2">
                {r ? <Chip tono={r.ok ? "exito" : "peligro"}>{r.ok ? `OK · ${r.milisegundos} ms` : "Falla"}</Chip> : <Chip>Sin probar</Chip>}
                <Button variant="outline" size="sm" disabled={probando.has(s.nombre)} onClick={() => probar(s)}>{probando.has(s.nombre) ? "Probando…" : "Probar"}</Button>
              </span>
              {r && !r.ok && <span className="w-full font-mono text-xs break-all text-[var(--mis-danger)]">{r.detalle}</span>}
            </li>
          );
        })}
      </ul>
    </Tarjeta>
  );
}
