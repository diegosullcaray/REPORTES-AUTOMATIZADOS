"use client";

import { CircleCheck, CircleDashed, CircleX, ExternalLink, FolderOpen, Play } from "lucide-react";
import Link from "next/link";
import { useState, type ReactNode } from "react";
import { Confirmar } from "@/components/confirmar";
import { Aviso, Chip, ErrorEnLinea } from "@/components/estados";
import { Terminal } from "@/components/terminal";
import { Button, buttonVariants } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, enCurso, errorDeCorte, fecha } from "@/lib/formato";
import type { Correo, ReporteDetalle, Verificacion } from "@/lib/tipos";
import { CampoCorte } from "./campo-corte";

interface Props {
  reporte: ReporteDetalle;
  corte: string;
  onCorte: (v: string) => void;
  verificacion: Verificacion | null;
  onIrAValidar: () => void;
  onVerArchivos: () => void;
}

function Paso({ estado, children }: { estado: "ok" | "pendiente" | "mal"; children: ReactNode }) {
  const Icono = estado === "ok" ? CircleCheck : estado === "mal" ? CircleX : CircleDashed;
  const color = estado === "ok" ? "var(--mis-success)" : estado === "mal" ? "var(--mis-danger)" : "var(--mis-text-tertiary)";
  return <li className="flex items-start gap-2"><Icono className="mt-0.5 size-4 shrink-0" style={{ color }} /><span>{children}</span></li>;
}

/** Parámetros + botón principal + log en vivo. La API vuelve a validar todo antes de encolar. */
export function PanelEjecucion({ reporte, corte, onCorte, verificacion, onIrAValidar, onVerArchivos }: Props) {
  const [forzar, setForzar] = useState(false);
  const [escritura, setEscritura] = useState(false);
  const [correo, setCorreo] = useState<Correo>("prueba");
  const [confirmando, setConfirmando] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [id, setId] = useState<string | null>(null);
  const { datos: x } = useConsulta(id && `ejecucion/${id}`, () => api.ejecucion(id!), (d) => enCurso(d.estado), 1500);

  const errorCorte = errorDeCorte(reporte.frecuencia, corte);
  const vigente = verificacion?.corte === corte ? verificacion : null;
  const tablasMal = !!vigente && !vigente.listo;
  const corriendo = !!x && enCurso(x.estado);
  const bloqueado = !!errorCorte || (reporte.escribe_en_bd && !escritura) || (tablasMal && !forzar) || corriendo;

  async function ejecutar() {
    setEnviando(true);
    setError(null);
    try {
      const nueva = await api.ejecutar({
        reporte: reporte.nombre, fecha_corte: corte || null, forzar, confirmar_escritura: escritura,
        correo: reporte.envia_correo ? correo : "no",
      });
      setId(nueva.id);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setEnviando(false);
      setConfirmando(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <section className="flex flex-col gap-4 rounded-lg border bg-card p-4">
        <h2 className="text-sm font-medium">Parámetros</h2>
        <CampoCorte reporte={reporte} valor={corte} onCambio={onCorte} />

        {reporte.envia_correo && (
          <fieldset className="flex flex-col gap-2">
            <legend className="mb-1 text-sm font-medium">Correo</legend>
            {([["prueba", "Enviar la PRUEBA solo a mi correo"], ["no", "Solo generar el Excel"]] as const).map(([v, t]) => (
              <label key={v} className="flex items-center gap-2 text-sm">
                <input type="radio" name="correo" value={v} checked={correo === v} onChange={() => setCorreo(v)} className="accent-[var(--mis-primary)]" />
                {t}
              </label>
            ))}
          </fieldset>
        )}
        {reporte.avisos.map((a) => <Aviso key={a}>{a}</Aviso>)}
        {reporte.escribe_en_bd && (
          <Opcion id="escritura" marcado={escritura} onCambio={setEscritura}
            titulo="Confirmo que este reporte crea/borra tablas permanentes"
            detalle="No lo ejecutes a la vez desde la consola: dos ejecuciones simultáneas se pisan." />
        )}
        {reporte.es_lote && tablasMal && (
          <Opcion id="forzar" marcado={forzar} onCambio={setForzar}
            titulo="Ejecutar aunque haya tablas desactualizadas (--forzar)"
            detalle="El resultado puede salir plausible y equivocado. Revisa el Excel antes de entregarlo." />
        )}

        <ul className="flex flex-col gap-1.5 text-sm text-muted-foreground">
          <Paso estado={errorCorte ? "mal" : "ok"}>Fecha de corte {corte && !errorCorte ? fecha(corte) : "pendiente"}</Paso>
          {reporte.es_lote ? (
            <Paso estado={!vigente ? "pendiente" : vigente.listo ? "ok" : "mal"}>
              {!vigente ? <>Tablas sin verificar · <button className="underline" onClick={onIrAValidar}>verificar ahora</button> (el reporte igual se detiene si falta alguna)</>
                : vigente.listo ? "Tablas al día al corte" : "Hay tablas desactualizadas: pide la carga a Producción"}
            </Paso>
          ) : (
            <Paso estado="pendiente">Lógica propia: no verifica tablas antes de ejecutar</Paso>
          )}
        </ul>

        {error && <ErrorEnLinea titulo="La API rechazó la ejecución" detalle={error} />}
        <div>
          <Button onClick={() => setConfirmando(true)} disabled={bloqueado || enviando}><Play /> Ejecutar reporte</Button>
        </div>
      </section>

      {id && (
        <Terminal titulo={`python main.py ${x?.argumentos.join(" ") ?? reporte.nombre}`} texto={x?.log ?? ""}
          estado={x && <Chip tono={ESTADO_EJECUCION[x.estado].tono}>{ESTADO_EJECUCION[x.estado].texto}</Chip>} />
      )}
      {x && !enCurso(x.estado) && (
        <div className="flex flex-wrap gap-2">
          {x.archivos.length > 0 && <Button variant="outline" size="sm" onClick={onVerArchivos}><FolderOpen /> Ver archivos ({x.archivos.length})</Button>}
          <Link href={`/ejecuciones/${x.id}`} className={buttonVariants({ variant: "ghost", size: "sm" })}><ExternalLink /> Detalle de la ejecución</Link>
        </div>
      )}

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
    <div className="flex items-start gap-3 rounded-lg border p-3" style={{ background: "var(--mis-warning-light)", borderColor: "color-mix(in srgb, var(--mis-warning) 30%, transparent)" }}>
      <Checkbox id={id} checked={marcado} onCheckedChange={(v) => onCambio(v === true)} className="mt-0.5" />
      <Label htmlFor={id} className="flex flex-col items-start gap-1">
        <span className="font-medium text-[var(--mis-warning)]">{titulo}</span>
        <span className="text-xs font-normal text-muted-foreground">{detalle}</span>
      </Label>
    </div>
  );
}
