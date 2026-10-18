"use client";

import { Copy, MessageSquare, PenBox, Play, Save } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";
import { Confirmar } from "@/components/confirmar";
import { Aviso, Chip, ErrorEnLinea } from "@/components/estados";
import { Tarjeta } from "@/components/tarjeta";
import { Terminal } from "@/components/terminal";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, enCurso, errorDeCorte, fecha } from "@/lib/formato";
import type { Correo, ReporteDetalle } from "@/lib/tipos";

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

/** Envío del archivo generado por Google Chat: casilla y a quién (se guarda en el .env). */
function EntregaChat({ reporte, marcado, onMarcado, destinatarios, onDestinatarios }: {
  reporte: string; marcado: boolean; onMarcado: (v: boolean) => void; destinatarios: string[]; onDestinatarios: (d: string[]) => void;
}) {
  const [editando, setEditando] = useState(!destinatarios.length);
  const [valor, setValor] = useState(destinatarios.join(", "));
  const [guardando, setGuardando] = useState(false);

  async function guardar() {
    setGuardando(true);
    try {
      const r = await api.guardarChatReporte(reporte, valor);
      onDestinatarios(r.chat_destinatarios);
      onMarcado(r.chat_destinatarios.length > 0);
      setEditando(!r.chat_destinatarios.length);
      toast.success("Destinatario guardado en el .env");
    } catch (e) {
      toast.error("No se guardó", { description: (e as Error).message });
    } finally {
      setGuardando(false);
    }
  }

  return (
    <fieldset className="flex flex-col gap-2 rounded-lg border p-3">
      <legend className="px-1 text-sm font-medium">Google Chat</legend>
      <label className="flex items-start gap-3 text-sm">
        <Checkbox checked={marcado} disabled={!destinatarios.length} onCheckedChange={(v) => onMarcado(v === true)} className="mt-0.5" />
        <span className="flex flex-col gap-0.5">
          <span className="flex items-center gap-1.5 font-medium"><MessageSquare className="size-4 text-muted-foreground" /> Enviar el archivo generado por Chat</span>
          <span className="text-xs text-muted-foreground">
            {destinatarios.length ? <>Mensaje directo con el archivo adjunto a <b>{destinatarios.join(", ")}</b>, con tu cuenta de Google (MCP).</> : "Indica a quién enviarlo."}
          </span>
        </span>
        {!editando && <Button type="button" variant="ghost" size="sm" className="ml-auto" onClick={() => setEditando(true)}><PenBox /> Cambiar</Button>}
      </label>
      {editando && (
        <form className="flex gap-2" onSubmit={(ev) => { ev.preventDefault(); void guardar(); }}>
          <Input value={valor} onChange={(ev) => setValor(ev.target.value)} type="text" autoComplete="off" aria-label="Destinatarios de Google Chat" placeholder="compañero@confianza.pe (varios separados por coma)" />
          <Button type="submit" variant="secondary" disabled={guardando}><Save /> {guardando ? "Guardando…" : "Guardar"}</Button>
        </form>
      )}
    </fieldset>
  );
}

/**
 * Pestaña General (como «Deploy Settings» de Dokploy): Ejecutar y log en vivo,
 * y los parámetros de la ejecución. Lo demás (tipo, servidor, responsable) vive en el encabezado y en las pestañas. La API vuelve a validar todo antes de encolar.
 */
export function PanelGeneral({ reporte, corte }: { reporte: ReporteDetalle; corte: string }) {
  const [forzar, setForzar] = useState(false);
  const [escritura, setEscritura] = useState(false);
  const [correo, setCorreo] = useState<Correo>("prueba");
  const [destinatariosChat, setDestinatariosChat] = useState(reporte.chat_destinatarios ?? []);
  const [chat, setChat] = useState(reporte.envia_chat && (reporte.chat_destinatarios ?? []).length > 0);
  const [confirmando, setConfirmando] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [id, setId] = useState<string | null>(null);
  const { datos: x } = useConsulta(id && `ejecucion/${id}`, () => api.ejecucion(id!), (d) => enCurso(d.estado), 1500);

  const errorCorte = errorDeCorte(reporte.frecuencia, corte);
  const corriendo = !!x && enCurso(x.estado);
  const motivo = errorCorte ?? (reporte.escribe_en_bd && !escritura ? "Confirma la escritura en la base de datos." : null);

  async function ejecutar() {
    setEnviando(true);
    setError(null);
    try {
      const nueva = await api.ejecutar({
        reporte: reporte.nombre, fecha_corte: corte || null, forzar, confirmar_escritura: escritura,
        correo: reporte.envia_correo ? correo : "no", chat: reporte.envia_chat && chat,
      });
      setId(nueva.id);
      toast.success("Ejecución encolada", { description: `Corte ${fecha(corte)}` });
    } catch (e) {
      setError((e as Error).message);
      toast.error("La API rechazó la ejecución", { description: (e as Error).message });
    } finally {
      setEnviando(false);
      setConfirmando(false);
    }
  }

  return (
    <div className="flex flex-col gap-4">
      <Tarjeta titulo="Ejecución" descripcion={`Corte ${corte ? fecha(corte) : "—"}: se cambia en «Fecha de cierre» de la cabecera.`}>
        <div className="flex flex-wrap gap-3">
          <Button onClick={() => setConfirmando(true)} disabled={!!motivo || enviando || corriendo} title={motivo ?? undefined}>
            <Play /> {corriendo ? "Ejecutando…" : "Ejecutar"}
          </Button>
          <Button variant="outline" onClick={() => { navigator.clipboard.writeText(`python main.py ${reporte.nombre}${corte ? ` --fecha-corte ${corte}` : ""}${reporte.envia_chat && chat ? " --chat" : ""}`); toast.success("Comando copiado"); }}>
            <Copy /> Copiar comando
          </Button>
        </div>
        {motivo && <p className="text-sm text-muted-foreground">No se puede ejecutar aún: {motivo}</p>}
        {error && <ErrorEnLinea titulo="La API rechazó la ejecución" detalle={error} />}
        {id && (
          <Terminal titulo={`python main.py ${x?.argumentos.join(" ") ?? reporte.nombre}`} texto={x?.log ?? ""}
            estado={x && <Chip tono={ESTADO_EJECUCION[x.estado].tono}>{ESTADO_EJECUCION[x.estado].texto}</Chip>} />
        )}
      </Tarjeta>

      <Tarjeta titulo="Parámetros" descripcion="Condiciones de la próxima ejecución.">
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
          {reporte.envia_chat && (
            <EntregaChat reporte={reporte.nombre} marcado={chat} onMarcado={setChat} destinatarios={destinatariosChat} onDestinatarios={setDestinatariosChat} />
          )}
          {reporte.avisos.map((a) => <Aviso key={a}>{a}</Aviso>)}
          {reporte.escribe_en_bd && (
            <Opcion id="escritura" marcado={escritura} onCambio={setEscritura} titulo="Confirmo que este reporte crea/borra tablas permanentes"
              detalle="No lo ejecutes a la vez desde la consola: dos ejecuciones simultáneas se pisan." />
          )}
          {reporte.es_lote && x?.estado === "tablas_desactualizadas" && (
            <Opcion id="forzar" marcado={forzar} onCambio={setForzar} titulo="Ejecutar aunque haya tablas desactualizadas (--forzar)"
              detalle="El resultado puede salir plausible y equivocado. Revisa el Excel antes de entregarlo." />
          )}
          {reporte.tablas.length > 0 && (
            <p className="text-sm text-muted-foreground">
              Las tablas se validan en conjunto en <Link href={`/validacion${reporte.grupo === "erick" ? "?grupo=erick" : ""}`} className="underline">Validación de tablas</Link>.
              El reporte igual se detiene si falta alguna.
            </p>
          )}
        </Tarjeta>

      <Confirmar abierto={confirmando} onAbierto={setConfirmando} titulo={`Ejecutar «${reporte.nombre}»`} accion={enviando ? "Encolando…" : "Ejecutar"}
        deshabilitado={enviando} peligro={forzar || escritura} onConfirmar={ejecutar}
        descripcion={
          <ul className="list-disc space-y-1 pl-4 text-left">
            <li>Corte: <b>{fecha(corte) === "—" ? reporte.corte.origen : fecha(corte)}</b></li>
            <li>Servidor: {reporte.servidores.join(", ")}</li>
            {forzar && <li>Con <b>--forzar</b>: hay tablas desactualizadas.</li>}
            {escritura && <li>Escribe en la base de datos.</li>}
            {reporte.envia_correo && <li>{correo === "prueba" ? "Enviará la prueba a tu correo." : "Sin correo."}</li>}
            {reporte.envia_chat && <li>{chat ? <>Enviará el archivo por Google Chat a <b>{destinatariosChat.join(", ")}</b>.</> : "Sin envío por Google Chat."}</li>}
            <li>Se ejecuta en cola: uno a la vez.</li>
          </ul>
        } />
    </div>
  );
}
