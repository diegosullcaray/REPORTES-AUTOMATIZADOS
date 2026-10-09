"use client";

import { Bell, Mail, MessageSquare, PenBox, Send, Trash2 } from "lucide-react";
import { useState, type ReactNode } from "react";
import { toast } from "sonner";
import { Confirmar } from "@/components/confirmar";
import { Chip, EsqueletoFilas, ErrorEnLinea } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import type { Notificaciones, PedidoNotificaciones } from "@/lib/tipos";

type Canal = "correo" | "chat";

function Campo({ id, etiqueta, ayuda, children }: { id: string; etiqueta: string; ayuda?: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor={id}>{etiqueta}</Label>
      {children}
      {ayuda && <span className="text-xs text-muted-foreground">{ayuda}</span>}
    </div>
  );
}

/**
 * Formulario de un proveedor en un diálogo (como «Add Notification» de Dokploy): campos, «Probar» y «Guardar».
 * La clave y el webhook son de solo escritura: vacío = no se tocan; «Quitar» los borra del .env.
 */
function DialogoProveedor({ canal, n, abierto, onCerrar, onGuardado }: { canal: Canal; n: Notificaciones; abierto: boolean; onCerrar: () => void; onGuardado: () => void }) {
  const inicial = { smtp_host: n.smtp_host, smtp_port: String(n.smtp_port), smtp_user: n.smtp_user, remitente_nombre: n.remitente_nombre, correo_prueba: n.correo_prueba, smtp_clave: "", webhook: "" };
  const [v, setV] = useState(inicial);
  const [quitar, setQuitar] = useState<Set<keyof PedidoNotificaciones>>(new Set());
  const [ocupado, setOcupado] = useState<"guardar" | "probar" | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [confirmarChat, setConfirmarChat] = useState(false);

  const campos: (keyof PedidoNotificaciones)[] = canal === "correo" ? ["smtp_host", "smtp_port", "smtp_user", "remitente_nombre", "correo_prueba", "smtp_clave"] : ["webhook"];
  const cambios: PedidoNotificaciones = Object.fromEntries(campos.flatMap((k) => (quitar.has(k) ? [[k, ""]] : v[k] !== inicial[k] ? [[k, v[k]]] : [])));
  const hayCambios = Object.keys(cambios).length > 0;
  const ponerCampo = (k: keyof PedidoNotificaciones) => ({
    id: k, value: v[k], onChange: (ev: React.ChangeEvent<HTMLInputElement>) => { setV((x) => ({ ...x, [k]: ev.target.value })); setQuitar((q) => { const s = new Set(q); s.delete(k); return s; }); },
  });

  async function guardar(): Promise<boolean> {
    setOcupado("guardar");
    setError(null);
    try {
      await api.guardarNotificaciones(cambios);
      toast.success("Notificación guardada en el .env", { description: "Rige desde el próximo envío." });
      onGuardado();
      return true;
    } catch (e) {
      setError((e as Error).message);
      return false;
    } finally {
      setOcupado(null);
    }
  }

  async function probar() {
    // Se guarda primero lo pendiente: la prueba usa lo que está en el .env, no lo que hay en el formulario.
    if (hayCambios && !(await guardar())) return;
    setOcupado("probar");
    try {
      const r = await api.probarNotificacion(canal);
      if (r.ok) toast.success("Prueba enviada", { description: r.detalle });
      else toast.error("La prueba falló", { description: r.detalle });
    } catch (e) {
      toast.error("No se pudo probar", { description: (e as Error).message });
    } finally {
      setOcupado(null);
    }
  }

  const secreto = (k: "smtp_clave" | "webhook", configurado: boolean, props: { etiqueta: string; ayuda: string; placeholder: string }) => (
    <Campo id={k} etiqueta={props.etiqueta} ayuda={props.ayuda}>
      <div className="flex gap-2">
        <Input {...ponerCampo(k)} type="password" autoComplete="off" placeholder={quitar.has(k) ? "Se quitará al guardar" : configurado ? "•••••••• (configurada; escribe para reemplazar)" : props.placeholder} />
        {configurado && (
          <Button type="button" variant="outline" size="icon" aria-label={`Quitar ${props.etiqueta}`} aria-pressed={quitar.has(k)}
            onClick={() => { setQuitar((q) => { const s = new Set(q); if (s.has(k)) s.delete(k); else s.add(k); return s; }); setV((x) => ({ ...x, [k]: "" })); }}><Trash2 /></Button>
        )}
      </div>
    </Campo>
  );

  return (
    <Dialog open={abierto} onOpenChange={(a) => !a && onCerrar()}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{canal === "correo" ? "Correo (SMTP)" : "Google Chat"}</DialogTitle>
          <DialogDescription>
            {canal === "correo" ? "Cuenta con la que se envían los reportes. La prueba llega solo al correo de prueba, nunca a la lista." : "Webhook del espacio donde se avisa cada envío."}
          </DialogDescription>
        </DialogHeader>
        <form id="form-notificacion" onSubmit={(ev) => { ev.preventDefault(); if (hayCambios) void guardar().then((ok) => ok && onCerrar()); }} className="flex flex-col gap-4">
          {canal === "correo" ? (
            <>
              <div className="grid gap-4 sm:grid-cols-[1fr_7rem]">
                <Campo id="smtp_host" etiqueta="Servidor SMTP"><Input {...ponerCampo("smtp_host")} placeholder="smtp.gmail.com" /></Campo>
                <Campo id="smtp_port" etiqueta="Puerto"><Input {...ponerCampo("smtp_port")} inputMode="numeric" placeholder="465" /></Campo>
              </div>
              <Campo id="smtp_user" etiqueta="Cuenta de envío (usuario)"><Input {...ponerCampo("smtp_user")} type="email" placeholder="mis@empresa.pe" autoComplete="off" /></Campo>
              {secreto("smtp_clave", n.clave_configurada, { etiqueta: "Contraseña de aplicación", ayuda: "Solo se guarda en el .env; nunca se vuelve a mostrar.", placeholder: "Contraseña de aplicación" })}
              <div className="grid gap-4 sm:grid-cols-2">
                <Campo id="remitente_nombre" etiqueta="Nombre del remitente"><Input {...ponerCampo("remitente_nombre")} /></Campo>
                <Campo id="correo_prueba" etiqueta="Correo de prueba" ayuda="Recibe la prueba antes de enviar a la lista."><Input {...ponerCampo("correo_prueba")} type="email" /></Campo>
              </div>
            </>
          ) : secreto("webhook", n.webhook_configurado, { etiqueta: "URL del webhook", ayuda: "Solo se guarda en el .env; nunca se vuelve a mostrar.", placeholder: "https://…googleapis.com/v1/spaces/…" })}
          {error && <ErrorEnLinea titulo="No se guardó" detalle={error} />}
        </form>
        <DialogFooter className="sm:justify-between">
          <Button type="button" variant="secondary" disabled={!!ocupado || (canal === "chat" && !n.webhook_configurado && !hayCambios)}
            onClick={() => (canal === "chat" ? setConfirmarChat(true) : void probar())}><Send /> {ocupado === "probar" ? "Probando…" : "Probar"}</Button>
          <Button type="submit" form="form-notificacion" disabled={!hayCambios || !!ocupado}>{ocupado === "guardar" ? "Guardando…" : "Guardar"}</Button>
        </DialogFooter>
        <Confirmar abierto={confirmarChat} onAbierto={setConfirmarChat} titulo="Probar Google Chat" accion="Enviar aviso de prueba"
          descripcion="Se publicará un mensaje de prueba en el espacio de Google Chat del webhook; lo verán todos sus miembros." onConfirmar={() => { setConfirmarChat(false); void probar(); }} />
      </DialogContent>
    </Dialog>
  );
}

function Proveedor({ icono, nombre, detalle, estado, onConfigurar }: { icono: ReactNode; nombre: string; detalle: string; estado: ReactNode; onConfigurar: () => void }) {
  return (
    <div className="flex flex-wrap items-center gap-3 rounded-lg border p-4">
      <span className="flex size-10 shrink-0 items-center justify-center rounded-lg border bg-muted text-muted-foreground [&>svg]:size-5">{icono}</span>
      <div className="flex min-w-0 flex-1 flex-col gap-0.5">
        <span className="flex flex-wrap items-center gap-2 font-medium">{nombre}{estado}</span>
        <span className="truncate text-sm text-muted-foreground">{detalle}</span>
      </div>
      <Button variant="outline" size="sm" onClick={onConfigurar}><PenBox /> Configurar</Button>
    </div>
  );
}

/** Notificaciones (página «Notifications» de Dokploy): lista de proveedores y, por cada uno, un diálogo para configurarlo y probarlo. */
export function PanelNotificaciones() {
  const { datos: n, error, cargando, recargar } = useConsulta("notificaciones", api.notificaciones);
  const [abierto, setAbierto] = useState<Canal | null>(null);
  return (
    <Pagina>
      <Marco icono={<Bell />} titulo="Notificaciones" descripcion="Cuenta de correo con la que se envían los reportes y aviso a Google Chat. Se guardan en el .env y rigen desde el próximo envío.">
        {error ? <ErrorEnLinea titulo="No se pudieron leer las notificaciones" detalle={`${error} Si acabas de actualizar el sistema, reinicia la API.`} onReintentar={recargar} />
          : cargando && !n ? <EsqueletoFilas filas={2} alto="h-16" />
          : n && (
            <div className="flex flex-col gap-3">
              <Proveedor icono={<Mail />} nombre="Correo (SMTP)" onConfigurar={() => setAbierto("correo")}
                estado={<Chip tono={n.smtp_user && n.clave_configurada ? "exito" : "aviso"}>{n.smtp_user && n.clave_configurada ? "configurado" : "falta cuenta o contraseña"}</Chip>}
                detalle={`${n.smtp_user || "Sin cuenta"} · ${n.smtp_host}:${n.smtp_port} · prueba a ${n.correo_prueba}${n.destinatarios !== null ? ` · ${n.destinatarios} destinatarios` : ""}`} />
              <Proveedor icono={<MessageSquare />} nombre="Google Chat" onConfigurar={() => setAbierto("chat")}
                estado={<Chip tono={n.webhook_configurado ? "exito" : "neutro"}>{n.webhook_configurado ? "webhook configurado" : "sin webhook"}</Chip>}
                detalle={n.webhook_configurado ? "Avisa en el espacio cada vez que se envía el correo a la lista." : "Opcional: avisa en un espacio de Google Chat cuando se envía el correo."} />
              {(["correo", "chat"] as const).map((c) => (
                <DialogoProveedor key={`${c}-${abierto === c}`} canal={c} n={n} abierto={abierto === c} onCerrar={() => setAbierto(null)} onGuardado={recargar} />
              ))}
            </div>
          )}
      </Marco>
    </Pagina>
  );
}
