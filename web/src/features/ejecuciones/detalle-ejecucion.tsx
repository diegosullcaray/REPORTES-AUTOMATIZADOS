"use client";

import { ArrowLeft, Copy, ScrollText } from "lucide-react";
import Link from "next/link";
import { toast } from "sonner";
import { Punto } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Button, buttonVariants } from "@/components/ui/button";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, enCurso, titulo } from "@/lib/formato";
import { ContenidoEjecucion } from "./contenido-ejecucion";

export function DetalleEjecucion({ id }: { id: string }) {
  const { datos: x } = useConsulta(`ejecucion/${id}`, () => api.ejecucion(id), (d) => enCurso(d.estado), 1500);
  const comando = x && `python main.py ${x.argumentos.join(" ")}`;

  const acciones = x && (
    <>
      <Button variant="outline" size="sm" onClick={() => { navigator.clipboard.writeText(comando!); toast.success("Comando copiado"); }}><Copy /> Copiar comando</Button>
      <Link href={`/reportes/${x.reporte}`} className={buttonVariants({ variant: "outline", size: "sm" })}><ArrowLeft /> {titulo(x.reporte)}</Link>
    </>
  );

  return (
    <Pagina>
      <Marco icono={<ScrollText />} acciones={acciones}
        titulo={<span className="flex items-center gap-2">Ejecución {x && <Punto tono={ESTADO_EJECUCION[x.estado].tono} etiqueta={ESTADO_EJECUCION[x.estado].texto} latido={enCurso(x.estado)} />}</span>}
        descripcion={x ? titulo(x.reporte) : id}>
        <ContenidoEjecucion id={id} />
      </Marco>
    </Pagina>
  );
}
