"use client";

import { CircleCheck, CircleDashed, CircleX, Copy, FolderOpen, History, Play, ShieldCheck } from "lucide-react";
import { useState, type ReactNode } from "react";
import { toast } from "sonner";
import { Confirmar } from "@/components/confirmar";
import { Aviso, Chip, ErrorEnLinea } from "@/components/estados";
import { Tarjeta } from "@/components/tarjeta";
import { Terminal } from "@/components/terminal";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { ESTADO_EJECUCION, TIPO, enCurso, errorDeCorte, fecha } from "@/lib/formato";
import type { Correo, ReporteDetalle, Verificacion } from "@/lib/tipos";

type Pestana = "validacion" | "archivos" | "ejecuciones";

interface Props {
  reporte: ReporteDetalle;
  corte: string; // se elige una sola vez, junto a las pestañas
  verificacion: Verificacion | null;
  irA: (p: Pestana) => void;
}

function Paso({ estado, children }: { estado: "ok" | "pendiente" | "mal"; children: ReactNode }) {
  const Icono = estado === "ok" ? CircleCheck : estado === "mal" ? CircleX : CircleDashed;
  const color = estado === "ok" ? "var(--mis-success)" : estado === "mal" ? "var(--mis-danger)" : "var(--mis-text-tertiary)";
  return <li className="flex items-start gap-2"><Icono className="mt-0.5 size-4 shrink-0" style={{ color }} /><span>{children}</span></li>;
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

function Dato({ etiqueta, children }: { etiqueta: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <dt className="text-xs text-muted-foreground">{etiqueta}</dt>
      <dd className="text-sm font-medium">{children}</dd>
    </div>
  );
}

/**
 * Pestaña General (como «Deploy Settings» de Dokploy): acciones del reporte arriba, log en vivo,
 * parámetros de la ejecución e información del reporte. La API vuelve a validar todo antes de encolar.
 */
export function PanelGeneral({ reporte, corte, verificacion, irA }: Props) {
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
  const motivo = errorCorte ?? (reporte.escribe_en_bd && !escritura ? "Confirma la escritura en la base de datos." : tablasMal && !forzar ? "Hay tablas desactualizadas." : null);
  const verificables = reporte.tablas.filter((t) => t.verificable).length;

  async function ejecutar() {
    setEnviando(true);
    setError(null);
    try {
      const nueva = await api.ejecutar({
        reporte: reporte.nombre, fecha_corte: corte || null, forzar, confirmar_escritura: escritura,
        correo: reporte.envia_correo ? correo : "no",
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
      <Tarjeta titulo="Ejecución" descripcion="Valida las tablas al corte, ejecuta el reporte y revisa sus archivos.">
        <div className="grid grid-cols-2 gap-3 lg:flex lg:flex-wrap">
          <Button onClick={() => setConfirmando(true)} disabled={!!motivo || enviando || corriendo} title={motivo ?? undefined}>
            <Play /> {corriendo ? "Ejecutando…" : "Ejecutar"}
          </Button>
          {reporte.es_lote && <Button variant="secondary" onClick={() => irA("validacion")}><ShieldCheck /> Verificar tablas</Button>}
          <Button variant="secondary" onClick={() => irA("archivos")}><FolderOpen /> Archivos</Button>
          <Button variant="secondary" onClick={() => irA("ejecuciones")}><History /> Ejecuciones</Button>
          <Button variant="outline" onClick={() => { navigator.clipboard.writeText(`python main.py ${reporte.nombre}${corte ? ` --fecha-corte ${corte}` : ""}`); toast.success("Comando copiado"); }}>
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

      <Tarjeta titulo="Parámetros" descripcion="Se aplican a la próxima ejecución, con la fecha de corte elegida arriba.">
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
            <Opcion id="escritura" marcado={escritura} onCambio={setEscritura} titulo="Confirmo que este reporte crea/borra tablas permanentes"
              detalle="No lo ejecutes a la vez desde la consola: dos ejecuciones simultáneas se pisan." />
          )}
          {reporte.es_lote && tablasMal && (
            <Opcion id="forzar" marcado={forzar} onCambio={setForzar} titulo="Ejecutar aunque haya tablas desactualizadas (--forzar)"
              detalle="El resultado puede salir plausible y equivocado. Revisa el Excel antes de entregarlo." />
          )}
          <ul className="flex flex-col gap-1.5 text-sm text-muted-foreground">
            <Paso estado={errorCorte ? "mal" : "ok"}>Fecha de corte {corte && !errorCorte ? fecha(corte) : "pendiente"}</Paso>
            {reporte.es_lote ? (
              <Paso estado={!vigente ? "pendiente" : vigente.listo ? "ok" : "mal"}>
                {!vigente ? <>Tablas sin verificar · <button className="underline" onClick={() => irA("validacion")}>verificar ahora</button> (el reporte igual se detiene si falta alguna)</>
                  : vigente.listo ? "Tablas al día al corte" : "Hay tablas desactualizadas: pide la carga a Producción"}
              </Paso>
            ) : <Paso estado="pendiente">Lógica propia: no verifica tablas antes de ejecutar</Paso>}
          </ul>
        </Tarjeta>

        <Tarjeta titulo="Información">
          <dl className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-6">
            <Dato etiqueta="Nº del legado">{reporte.orden}</Dato>
            <Dato etiqueta="Tipo">{TIPO[reporte.frecuencia]}</Dato>
            <Dato etiqueta="Responsable">{reporte.grupo === "diarias" ? "—" : reporte.grupo === "piero" ? "Piero" : "Erick"}</Dato>
            <Dato etiqueta="Servidor"><span className="font-mono">{reporte.servidores.join(", ")}</span></Dato>
            <Dato etiqueta="Tablas">{reporte.tablas.length} ({verificables} con control de fecha)</Dato>
            <Dato etiqueta="Vacío">{reporte.vacio_valido ? "Es válido" : "Es error"}</Dato>
          </dl>
          <div className="flex flex-col gap-1">
            <span className="text-xs text-muted-foreground">Carpeta de salida</span>
            <code className="w-fit rounded-md bg-muted px-2 py-1 font-mono text-xs break-all">data/outputs/{reporte.carpeta}</code>
          </div>
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
            <li>Se ejecuta en cola: uno a la vez.</li>
          </ul>
        } />
    </div>
  );
}
