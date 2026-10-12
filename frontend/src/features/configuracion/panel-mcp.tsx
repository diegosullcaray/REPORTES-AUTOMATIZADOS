"use client";

import { Copy, MessageSquare, Plug, Send } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { toast } from "sonner";
import { Confirmar } from "@/components/confirmar";
import { Aviso, Chip, EsqueletoFilas, ErrorEnLinea } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import type { ServidorMcp } from "@/lib/tipos";

const copiar = (texto: string, aviso: string) => {
  navigator.clipboard.writeText(texto).then(() => toast.success(aviso), () => toast.error("No se pudo copiar"));
};

/** Un servidor MCP: estado, herramientas, configuración para el cliente y un envío manual de mensaje. */
function TarjetaServidor({ s }: { s: ServidorMcp }) {
  const [texto, setTexto] = useState("");
  const [confirmar, setConfirmar] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const json = JSON.stringify(s.configuracion, null, 2);
  const comandoClaude = `claude mcp add ${s.id} -- ${s.comando} ${s.args.map((a) => (a.includes(" ") ? `"${a}"` : a)).join(" ")}`;

  async function enviar() {
    setEnviando(true);
    try {
      const r = await api.enviarMensajeMcp(s.id, texto);
      if (r.ok) { toast.success("Mensaje enviado", { description: r.detalle }); setTexto(""); }
      else toast.error("No se envió", { description: r.detalle });
    } catch (e) {
      toast.error("No se pudo enviar", { description: (e as Error).message });
    } finally {
      setEnviando(false);
    }
  }

  return (
    <div className="flex flex-col gap-4 rounded-lg border p-4">
      <div className="flex flex-wrap items-center gap-3">
        <span className="flex size-10 shrink-0 items-center justify-center rounded-lg border bg-muted text-muted-foreground [&>svg]:size-5"><MessageSquare /></span>
        <div className="flex min-w-0 flex-1 flex-col gap-0.5">
          <span className="flex flex-wrap items-center gap-2 font-medium">
            {s.nombre} <Chip tono={s.webhook_configurado ? "exito" : "aviso"}>{s.webhook_configurado ? "webhook configurado" : "falta el webhook"}</Chip>
          </span>
          <span className="text-sm text-muted-foreground">{s.descripcion}</span>
        </div>
      </div>

      {!s.webhook_configurado && (
        <Aviso>El MCP usa el webhook de Google Chat del .env. Configúralo en <Link href="/configuracion/notificaciones" className="underline">Notificaciones</Link>.</Aviso>
      )}

      <section className="flex flex-col gap-2">
        <h3 className="text-sm font-medium">Herramientas</h3>
        <ul className="divide-y rounded-lg border">
          {s.herramientas.map((h) => (
            <li key={h.nombre} className="flex flex-col gap-0.5 px-3 py-2">
              <code className="text-sm font-medium">{h.nombre}</code>
              <span className="text-xs text-muted-foreground">{h.descripcion}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="flex flex-col gap-2">
        <div className="flex flex-wrap items-center justify-between gap-2">
          <h3 className="text-sm font-medium">Configuración para tu cliente MCP</h3>
          <span className="flex gap-2">
            <Button variant="outline" size="sm" onClick={() => copiar(json, "JSON copiado")}><Copy /> Copiar JSON</Button>
            <Button variant="outline" size="sm" onClick={() => copiar(comandoClaude, "Comando copiado")}><Copy /> Copiar comando de Claude Code</Button>
          </span>
        </div>
        <pre className="overflow-x-auto rounded-lg border bg-muted/40 p-3 font-mono text-xs">{json}</pre>
        <span className="text-xs text-muted-foreground">
          Pégalo en el <code>.mcp.json</code> del cliente. No lleva secretos: el servidor lee el webhook del .env. Usa el Python con el que instalaste el backend (aquí: <code>{s.python}</code>).
        </span>
      </section>

      <section className="flex flex-col gap-2">
        <Label htmlFor={`mensaje-${s.id}`}>Enviar un mensaje de prueba</Label>
        <textarea id={`mensaje-${s.id}`} value={texto} onChange={(ev) => setTexto(ev.target.value)} rows={3} maxLength={4000} placeholder="Escribe el mensaje a publicar en el espacio…"
          className="min-h-20 w-full rounded-lg border border-input bg-transparent px-2.5 py-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50" />
        <div className="flex justify-end">
          <Button disabled={!s.webhook_configurado || !texto.trim() || enviando} onClick={() => setConfirmar(true)}><Send /> {enviando ? "Enviando…" : "Enviar a Google Chat"}</Button>
        </div>
      </section>
      <Confirmar abierto={confirmar} onAbierto={setConfirmar} titulo="Enviar a Google Chat" accion="Enviar mensaje"
        descripcion="Se publicará el mensaje en el espacio de Google Chat del webhook; lo verán todos sus miembros." onConfirmar={() => { setConfirmar(false); void enviar(); }} />
    </div>
  );
}

/** Servidores MCP: qué hay, cómo conectarlo desde un cliente y cómo probarlo. */
export function PanelMcp() {
  const { datos, error, cargando, recargar } = useConsulta("mcp", api.mcp);
  return (
    <Pagina>
      <Marco icono={<Plug />} titulo="MCP" descripcion="Servidores MCP para que un asistente use los canales de la web. Hoy: enviar mensajes a Google Chat.">
        {error ? <ErrorEnLinea titulo="No se pudieron leer los servidores MCP" detalle={`${error} Si acabas de actualizar el sistema, reinicia la API.`} onReintentar={recargar} />
          : cargando && !datos ? <EsqueletoFilas filas={2} alto="h-24" />
          : <div className="flex flex-col gap-3">{datos?.map((s) => <TarjetaServidor key={s.id} s={s} />)}</div>}
      </Marco>
    </Pagina>
  );
}
