"use client";

import { MessageSquare, Save, Send } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";
import { Confirmar } from "@/components/confirmar";
import { Aviso, EsqueletoFilas, EstadoVacio, ErrorEnLinea } from "@/components/estados";
import { Hace } from "@/components/hace";
import { Tarjeta } from "@/components/tarjeta";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useConsulta, type Consulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import { fecha } from "@/lib/formato";
import type { EntradaValidacion } from "@/lib/tipos";
import { SolicitudProduccion } from "./solicitud-produccion";

/** A quién se le pide por Google Chat que actualice las tablas: se guarda en el .env y se envía a cada uno. */
function EnvioChat({ grupo, ultima, onEnviado }: { grupo: string; ultima: EntradaValidacion; onEnviado: () => void }) {
  const destinos = useConsulta(`validacion/${grupo}/chat`, () => api.destinosChatValidacion(grupo));
  const [valor, setValor] = useState<string | null>(null);
  const [abierto, setAbierto] = useState(false);
  const [ocupado, setOcupado] = useState<"guardar" | "enviar" | null>(null);
  const guardados = destinos.datos?.destinatarios ?? [];
  const texto = valor ?? guardados.join(", ");

  async function guardar() {
    setOcupado("guardar");
    try {
      const r = await api.guardarDestinosChatValidacion(grupo, texto);
      setValor(null);
      destinos.recargar();
      toast.success(r.destinatarios.length ? "Destinatarios guardados en el .env" : "Sin destinatarios");
    } catch (e) {
      toast.error("No se guardó", { description: (e as Error).message });
    } finally {
      setOcupado(null);
    }
  }

  async function enviar() {
    setOcupado("enviar");
    try {
      const r = await api.enviarChatValidacion(grupo);
      if (r.ok) toast.success("Mensaje enviado", { description: r.detalle }); else toast.error("No se envió a todos", { description: r.detalle });
    } catch (e) {
      toast.error("No se envió", { description: (e as Error).message });
    } finally {
      setOcupado(null);
      setAbierto(false);
      onEnviado();
    }
  }

  return (
    <Tarjeta titulo="Pedirlo por Google Chat" descripcion="Envía este mensaje a un compañero para que actualice las tablas, con tu cuenta de Google (MCP › Google Workspace).">
      {destinos.error ? <ErrorEnLinea titulo="No se pudo leer a quién se envía" detalle={destinos.error} onReintentar={destinos.recargar} />
        : destinos.cargando && !destinos.datos ? <EsqueletoFilas filas={1} /> : (
          <>
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="chat-destinos">Correo del compañero (varios separados por coma)</Label>
              <div className="flex gap-2">
                <Input id="chat-destinos" value={texto} onChange={(ev) => setValor(ev.target.value)} autoComplete="off" placeholder="compañero@confianza.pe" />
                <Button type="button" variant="outline" disabled={valor === null || !!ocupado} onClick={() => void guardar()}><Save /> {ocupado === "guardar" ? "Guardando…" : "Guardar"}</Button>
              </div>
            </div>
            {ultima.chat_enviado && <Aviso tono="exito">Ya se envió a {ultima.chat_a.join(", ")} <Hace iso={ultima.chat_enviado} />. Si siguen faltando tablas, vuelve a verificar.</Aviso>}
            <div className="flex justify-end">
              <Button type="button" disabled={!guardados.length || valor !== null || !!ocupado} onClick={() => setAbierto(true)}><Send /> {ocupado === "enviar" ? "Enviando…" : "Enviar por Google Chat"}</Button>
            </div>
          </>
        )}
      <Confirmar abierto={abierto} onAbierto={setAbierto} titulo="Enviar por Google Chat" accion="Enviar" deshabilitado={!!ocupado} onConfirmar={() => void enviar()}
        descripcion={<>Se enviará de verdad a <b>{guardados.join(", ")}</b> el mensaje de la verificación al corte {fecha(ultima.corte)}.</>} />
    </Tarjeta>
  );
}

/** Mensaje de la última verificación con las tablas que faltan, para copiarlo o enviarlo por Chat. */
export function MensajeValidacion({ grupo, historial }: { grupo: string; historial: Consulta<EntradaValidacion[]> }) {
  const ultima = historial.datos?.[0];
  return historial.error ? <ErrorEnLinea titulo="No se pudo leer el historial" detalle={historial.error} onReintentar={historial.recargar} />
    : historial.cargando && !historial.datos ? <EsqueletoFilas filas={3} />
    : !ultima ? <EstadoVacio icono={MessageSquare} titulo="Aún no hay mensaje" descripcion="Verifica las tablas en la pestaña Validación: si falta alguna, aquí queda el mensaje para pedir que la actualicen." />
    : !ultima.solicitud ? <Aviso tono="exito">En la última verificación (corte {fecha(ultima.corte)}, <Hace iso={ultima.ejecutada} />) todo estaba al día: no hay nada que pedir.</Aviso>
    : (
      <div className="flex flex-col gap-4">
        <p className="text-sm text-muted-foreground">De la última verificación: corte {fecha(ultima.corte)}, <Hace iso={ultima.ejecutada} />.</p>
        <SolicitudProduccion texto={ultima.solicitud} guardar={() => api.guardarSolicitudGrupo(grupo, ultima.corte)} />
        <EnvioChat grupo={grupo} ultima={ultima} onEnviado={historial.recargar} />
      </div>
    );
}
