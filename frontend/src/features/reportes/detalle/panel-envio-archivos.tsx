"use client";

import { FileSpreadsheet, Save, Send } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Confirmar } from "@/components/confirmar";
import { Aviso, EsqueletoFilas, EstadoVacio, ErrorEnLinea } from "@/components/estados";
import { Tarjeta } from "@/components/tarjeta";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { tamano, titulo } from "@/lib/formato";
import type { ReporteDetalle } from "@/lib/tipos";

const lista = (texto: string) => texto.split(",").map((c) => c.trim()).filter(Boolean);
const CLASE_TEXTO = "w-full rounded-lg border border-input bg-transparent px-2.5 py-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50";

/** Firma de Gmail de la cuenta autorizada, en un iframe aislado (es HTML de terceros: sin scripts ni acceso a la página). */
function VistaFirma() {
  const { datos, error, cargando, recargar } = useConsulta("google/firma", api.firmaGmail);
  if (error) return <ErrorEnLinea titulo="No se pudo leer tu firma de Gmail" detalle={error} onReintentar={recargar} />;
  if (cargando && !datos) return <EsqueletoFilas filas={1} alto="h-20" />;
  if (!datos?.html) return <Aviso tono="neutro">Tu cuenta no tiene firma en Gmail (Configuración › Ver toda la configuración › Firma).</Aviso>;
  return <iframe title="Firma de Gmail" sandbox="" srcDoc={datos.html} className="h-32 w-full rounded-lg border bg-white" />;
}

/** Correo con los archivos generados del reporte: destinatarios y copia (se guardan en el .env), archivos elegidos y tu firma de Gmail. */
export function PanelEnvioArchivos({ reporte }: { reporte: ReporteDetalle }) {
  const archivos = useConsulta(`archivos/${reporte.nombre}`, () => api.archivos(reporte.nombre));
  const [para, setPara] = useState(reporte.correo_para.join(", "));
  const [cc, setCc] = useState(reporte.correo_cc.join(", "));
  const [asunto, setAsunto] = useState(titulo(reporte.nombre));
  const [mensaje, setMensaje] = useState("Buenos días,\n\nAdjunto el reporte.\n");
  const [elegidos, setElegidos] = useState<string[] | null>(null);
  const [conFirma, setConFirma] = useState(true);
  const [abierto, setAbierto] = useState(false);
  const [conforme, setConforme] = useState(false);
  const [ocupado, setOcupado] = useState<"guardar" | "prueba" | "enviar" | null>(null);

  const disponibles = archivos.datos ?? [];
  const marcados = elegidos ?? (disponibles[0] ? [disponibles[0].nombre] : []); // por defecto, el más reciente
  const alternar = (n: string, v: boolean) => setElegidos(v ? [...marcados, n] : marcados.filter((x) => x !== n));
  const completo = lista(para).length > 0 && asunto.trim() !== "" && marcados.length > 0;

  async function guardar() {
    setOcupado("guardar");
    try {
      const r = await api.guardarDestinosCorreo(reporte.nombre, para, cc);
      setPara(r.correo_para.join(", "));
      setCc(r.correo_cc.join(", "));
      toast.success("Destinatarios guardados en el .env");
    } catch (e) {
      toast.error("No se guardó", { description: (e as Error).message });
    } finally {
      setOcupado(null);
    }
  }

  async function enviar(prueba: boolean) {
    setOcupado(prueba ? "prueba" : "enviar");
    try {
      const r = await api.enviarArchivosCorreo(reporte.nombre, { para: lista(para), cc: lista(cc), asunto: asunto.trim(), mensaje, archivos: marcados, con_firma: conFirma, prueba });
      if (r.ok) toast.success(prueba ? "Prueba enviada" : "Correo enviado", { description: r.detalle }); else toast.error("No se envió", { description: r.detalle });
    } catch (e) {
      toast.error("No se envió", { description: (e as Error).message });
    } finally {
      setOcupado(null);
      setAbierto(false);
    }
  }

  return (
    <Tarjeta titulo="Enviar archivos por correo" descripcion="Con tu cuenta de Google y tu firma de Gmail. Primero envíate una prueba y, si estás conforme, envía a la lista.">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="correo-para">Para</Label>
          <Input id="correo-para" value={para} onChange={(ev) => setPara(ev.target.value)} autoComplete="off" placeholder="ana@empresa.pe, luis@empresa.pe" />
        </div>
        <div className="flex flex-col gap-1.5">
          <Label htmlFor="correo-cc">Con copia (CC)</Label>
          <Input id="correo-cc" value={cc} onChange={(ev) => setCc(ev.target.value)} autoComplete="off" placeholder="jefe@empresa.pe" />
        </div>
      </div>
      <div className="flex justify-end">
        <Button type="button" variant="outline" size="sm" disabled={!!ocupado} onClick={() => void guardar()}><Save /> {ocupado === "guardar" ? "Guardando…" : "Guardar destinatarios"}</Button>
      </div>

      <div className="flex flex-col gap-1.5">
        <Label htmlFor="correo-asunto">Asunto</Label>
        <Input id="correo-asunto" value={asunto} onChange={(ev) => setAsunto(ev.target.value)} maxLength={200} />
      </div>
      <div className="flex flex-col gap-1.5">
        <Label htmlFor="correo-mensaje">Mensaje</Label>
        <textarea id="correo-mensaje" value={mensaje} onChange={(ev) => setMensaje(ev.target.value)} rows={5} maxLength={10000} className={CLASE_TEXTO} />
      </div>

      <fieldset className="flex flex-col gap-2 rounded-lg border p-3">
        <legend className="px-1 text-sm font-medium">Archivos a adjuntar</legend>
        {archivos.error ? <ErrorEnLinea titulo="No se pudieron listar los archivos" detalle={archivos.error} onReintentar={archivos.recargar} />
          : archivos.cargando && !archivos.datos ? <EsqueletoFilas filas={3} />
          : !disponibles.length ? <EstadoVacio icono={FileSpreadsheet} titulo="Aún no hay archivos" descripcion="Ejecuta el reporte para generar el Excel y adjuntarlo." />
          : disponibles.map((a) => (
            <label key={a.nombre} className="flex cursor-pointer items-center gap-3 text-sm">
              <Checkbox checked={marcados.includes(a.nombre)} onCheckedChange={(v) => alternar(a.nombre, v === true)} />
              <span className="min-w-0 flex-1 truncate" title={a.nombre}>{a.nombre}</span>
              <span className="text-xs text-muted-foreground">{tamano(a.tamano)}</span>
            </label>
          ))}
      </fieldset>

      <fieldset className="flex flex-col gap-2 rounded-lg border p-3">
        <legend className="px-1 text-sm font-medium">Firma</legend>
        <label className="flex items-center gap-3 text-sm">
          <Checkbox checked={conFirma} onCheckedChange={(v) => setConFirma(v === true)} />
          Incluir mi firma de Gmail al final del correo
        </label>
        {conFirma && <VistaFirma />}
      </fieldset>

      <div className="flex flex-wrap justify-end gap-2">
        <Button type="button" variant="outline" disabled={!completo || !!ocupado} onClick={() => void enviar(true)}>{ocupado === "prueba" ? "Enviando prueba…" : "Enviarme una prueba"}</Button>
        <Button type="button" disabled={!completo || !!ocupado} onClick={() => { setConforme(false); setAbierto(true); }}><Send /> Enviar a la lista</Button>
      </div>

      <Confirmar abierto={abierto} onAbierto={setAbierto} titulo="Enviar correo" accion={ocupado === "enviar" ? "Enviando…" : "Enviar"} deshabilitado={!conforme || !!ocupado} onConfirmar={() => void enviar(false)}
        descripcion={<>Se enviará de verdad desde tu cuenta de Google a <b>{lista(para).join(", ")}</b>{lista(cc).length > 0 && <> (copia: {lista(cc).join(", ")})</>} con {marcados.length} archivo(s).</>}>
        <div className="flex items-start gap-3">
          <Checkbox id="conforme-archivos" checked={conforme} onCheckedChange={(v) => setConforme(v === true)} className="mt-0.5" />
          <Label htmlFor="conforme-archivos" className="font-normal">Revisé la prueba y estoy conforme.</Label>
        </div>
      </Confirmar>
    </Tarjeta>
  );
}
