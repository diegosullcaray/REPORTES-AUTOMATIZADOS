"use client";

import { Send } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { Confirmar } from "@/components/confirmar";
import { Aviso, EsqueletoFilas, ErrorEnLinea } from "@/components/estados";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { errorDeCorte, fecha } from "@/lib/formato";
import type { ReporteDetalle } from "@/lib/tipos";
import { CampoCorte } from "./campo-corte";

/** Paso 4: prueba -> conforme -> todos. Reutiliza el Excel e imagen de la prueba; no vuelve a consultar. */
export function PanelCorreo({ reporte, corte, onCorte }: { reporte: ReporteDetalle; corte: string; onCorte: (v: string) => void }) {
  const router = useRouter();
  const valido = !errorDeCorte(reporte.frecuencia, corte);
  const { datos, error, cargando, recargar } = useConsulta(valido ? `envio/${reporte.nombre}/${corte}` : null, () => api.estadoEnvio(reporte.nombre, corte || null));
  const [abierto, setAbierto] = useState(false);
  const [conforme, setConforme] = useState(false);
  const [errorEnvio, setErrorEnvio] = useState<string | null>(null);

  async function enviarATodos() {
    setErrorEnvio(null);
    try {
      const x = await api.ejecutar({ reporte: reporte.nombre, fecha_corte: corte || null, correo: "todos", conforme: true });
      router.push(`/ejecuciones/${x.id}`);
    } catch (e) {
      setErrorEnvio((e as Error).message);
      setAbierto(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <CampoCorte reporte={reporte} valor={corte} onCambio={onCorte} />
      <ol className="list-decimal space-y-1 pl-5 text-[13px] text-[var(--mis-text-secondary)]">
        <li>Ejecuta el reporte con «Enviar el correo de PRUEBA»: llega solo a tu correo.</li>
        <li>Revisa el correo, la imagen del resumen y el Excel (pestaña Archivos).</li>
        <li>Si estás conforme, envía ese mismo correo a toda la lista desde aquí.</li>
      </ol>

      {!valido ? null : error ? (
        <ErrorEnLinea titulo="No se pudo leer el estado del envío" detalle={error} onReintentar={recargar} />
      ) : cargando && !datos ? (
        <EsqueletoFilas filas={2} />
      ) : datos && (
        <>
          <dl className="rounded-lg border bg-card grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 p-3 text-[13px]">
            <dt className="text-[var(--mis-text-secondary)]">Prueba enviada</dt><dd>{fecha(datos.prueba)}</dd>
            <dt className="text-[var(--mis-text-secondary)]">Enviado a todos</dt><dd>{fecha(datos.todos)}</dd>
            <dt className="text-[var(--mis-text-secondary)]">Excel</dt><dd className="truncate">{datos.excel ?? "—"}</dd>
          </dl>
          {datos.todos ? (
            <Aviso tono="exito">Ya se envió a toda la lista el {fecha(datos.todos)}.</Aviso>
          ) : !datos.prueba ? (
            <Aviso tono="neutro">Aún no hay correo de prueba para {fecha(datos.corte)}. Ejecuta primero el reporte.</Aviso>
          ) : (
            <div><Button onClick={() => { setConforme(false); setAbierto(true); }}><Send /> Enviar a toda la lista</Button></div>
          )}
        </>
      )}
      {errorEnvio && <ErrorEnLinea titulo="No se pudo enviar" detalle={errorEnvio} />}

      <Confirmar abierto={abierto} onAbierto={setAbierto} titulo="Enviar a toda la lista" accion="Enviar" deshabilitado={!conforme} onConfirmar={enviarATodos}
        descripcion={<>Se enviará con la cuenta MIS el correo de la prueba del {fecha(datos?.prueba)} y se avisará a Google Chat.</>}>
        <div className="flex items-start gap-3">
          <Checkbox id="conforme" checked={conforme} onCheckedChange={(v) => setConforme(v === true)} className="mt-0.5" />
          <Label htmlFor="conforme" className="font-normal">Revisé el correo de prueba y estoy conforme.</Label>
        </div>
      </Confirmar>
    </div>
  );
}
