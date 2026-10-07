"use client";

import { CircleCheck, CircleDashed, CircleX, Play } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, type ReactNode } from "react";
import { Confirmar } from "@/components/confirmar";
import { Aviso, ErrorEnLinea } from "@/components/estados";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";
import { errorDeCorte, fecha } from "@/lib/formato";
import type { Correo, ReporteDetalle, Verificacion } from "@/lib/tipos";
import { CampoCorte } from "./campo-corte";

interface Props {
  reporte: ReporteDetalle;
  corte: string;
  onCorte: (v: string) => void;
  verificacion: Verificacion | null;
  onIrAValidar: () => void;
}

function Paso({ estado, children }: { estado: "ok" | "pendiente" | "mal"; children: ReactNode }) {
  const Icono = estado === "ok" ? CircleCheck : estado === "mal" ? CircleX : CircleDashed;
  const color = estado === "ok" ? "var(--mis-success)" : estado === "mal" ? "var(--mis-danger)" : "var(--mis-text-tertiary)";
  return <li className="flex items-start gap-2 text-[13px]"><Icono className="mt-0.5 size-4 shrink-0" style={{ color }} /><span>{children}</span></li>;
}

/** Paso 2: lista de control + opciones del reporte + confirmación. La API vuelve a validar todo. */
export function PanelEjecucion({ reporte, corte, onCorte, verificacion, onIrAValidar }: Props) {
  const router = useRouter();
  const [forzar, setForzar] = useState(false);
  const [escritura, setEscritura] = useState(false);
  const [correo, setCorreo] = useState<Correo>("prueba");
  const [confirmando, setConfirmando] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const errorCorte = errorDeCorte(reporte.frecuencia, corte);
  const vigente = verificacion?.corte === corte ? verificacion : null;
  const tablasMal = !!vigente && !vigente.listo;
  const bloqueado = !!errorCorte || (reporte.escribe_en_bd && !escritura) || (tablasMal && !forzar);

  async function ejecutar() {
    setEnviando(true);
    setError(null);
    try {
      const x = await api.ejecutar({
        reporte: reporte.nombre, fecha_corte: corte || null, forzar, confirmar_escritura: escritura,
        correo: reporte.envia_correo ? correo : "no",
      });
      router.push(`/ejecuciones/${x.id}`);
    } catch (e) {
      setError((e as Error).message);
      setConfirmando(false);
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <CampoCorte reporte={reporte} valor={corte} onCambio={onCorte} />

      <ol className="mis-superficie flex flex-col gap-2 p-3">
        <Paso estado={errorCorte ? "mal" : "ok"}>Fecha de corte válida{corte && !errorCorte && `: ${fecha(corte)}`}</Paso>
        {reporte.es_lote ? (
          <Paso estado={!vigente ? "pendiente" : vigente.listo ? "ok" : "mal"}>
            {!vigente ? <>Tablas sin verificar para esta fecha. <button className="underline" onClick={onIrAValidar}>Verificar ahora</button> (el reporte igual se detiene si falta alguna).</>
              : vigente.listo ? "Tablas al día al corte." : "Hay tablas desactualizadas: pide la actualización a Producción antes de ejecutar."}
          </Paso>
        ) : (
          <Paso estado="pendiente">Reporte con lógica propia: no verifica tablas antes de ejecutar. Revisa el paso 1 por tu cuenta.</Paso>
        )}
        {reporte.escribe_en_bd && <Paso estado={escritura ? "ok" : "mal"}>Confirmación de escritura en la base de datos.</Paso>}
      </ol>

      {reporte.avisos.map((a) => <Aviso key={a}>{a}</Aviso>)}

      {reporte.escribe_en_bd && (
        <Opcion id="escritura" marcado={escritura} onCambio={setEscritura}
          titulo="Confirmo que este reporte crea/borra tablas permanentes"
          detalle="No lo ejecutes a la vez desde la consola: dos ejecuciones simultáneas se pisan." />
      )}
      {reporte.es_lote && tablasMal && (
        <Opcion id="forzar" marcado={forzar} onCambio={setForzar}
          titulo="Ejecutar aunque haya tablas desactualizadas (--forzar)"
          detalle="El resultado puede salir plausible y equivocado. Úsalo solo si lo decidiste y revisa el Excel antes de entregarlo." />
      )}
      {reporte.envia_correo && (
        <fieldset className="flex flex-col gap-2">
          <legend className="mb-1 text-[13px] font-medium">Después de generar el Excel</legend>
          {([["prueba", "Enviar el correo de PRUEBA solo a mi correo (recomendado)"], ["no", "Solo generar el Excel, sin correo"]] as const).map(([v, t]) => (
            <label key={v} className="flex items-center gap-2 text-[13px]">
              <input type="radio" name="correo" value={v} checked={correo === v} onChange={() => setCorreo(v)} className="accent-[var(--mis-primary)]" />
              {t}
            </label>
          ))}
          <span className="text-[12px] text-[var(--mis-text-tertiary)]">El envío a toda la lista se hace en la pestaña Correo, con la prueba ya revisada.</span>
        </fieldset>
      )}

      {error && <ErrorEnLinea titulo="La API rechazó la ejecución" detalle={error} />}

      <div>
        <Button size="lg" onClick={() => setConfirmando(true)} disabled={bloqueado || enviando}><Play /> Ejecutar reporte</Button>
      </div>

      <Confirmar abierto={confirmando} onAbierto={setConfirmando} titulo={`Ejecutar «${reporte.nombre}»`} accion={enviando ? "Encolando…" : "Ejecutar"}
        deshabilitado={enviando} peligro={forzar || escritura} onConfirmar={ejecutar}
        descripcion={
          <ul className="list-disc space-y-1 pl-4 text-left">
            <li>Corte: <b>{fecha(corte) === "—" ? reporte.corte.origen : fecha(corte)}</b></li>
            <li>Servidor: {reporte.servidores.join(", ")}</li>
            {forzar && <li>Con <b>--forzar</b>: hay tablas desactualizadas.</li>}
            {escritura && <li>Escribe en la base de datos.</li>}
            {reporte.envia_correo && <li>{correo === "prueba" ? "Enviará la prueba a tu correo." : "Sin correo."}</li>}
            <li>Se ejecuta en cola: uno a la vez.</li>
          </ul>
        } />
    </div>
  );
}

function Opcion({ id, marcado, onCambio, titulo, detalle }: { id: string; marcado: boolean; onCambio: (v: boolean) => void; titulo: string; detalle: string }) {
  return (
    <div className="flex items-start gap-3 rounded-[10px] border p-3" style={{ background: "var(--mis-warning-light)", borderColor: "color-mix(in srgb, var(--mis-warning) 30%, transparent)" }}>
      <Checkbox id={id} checked={marcado} onCheckedChange={(v) => onCambio(v === true)} className="mt-0.5" />
      <Label htmlFor={id} className="flex flex-col items-start gap-1">
        <span className="font-medium text-[var(--mis-warning)]">{titulo}</span>
        <span className="text-[12px] font-normal text-[var(--mis-text-secondary)]">{detalle}</span>
      </Label>
    </div>
  );
}
