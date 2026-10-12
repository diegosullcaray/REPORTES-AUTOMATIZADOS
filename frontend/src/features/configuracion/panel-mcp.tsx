"use client";

import { Copy, ExternalLink, FlaskConical, KeyRound, LogOut, Plug, Save, Trash2, Undo2 } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState, type ReactNode } from "react";
import { toast } from "sonner";
import { FilaAjuste, SeccionAjustes } from "@/components/ajustes";
import { Confirmar } from "@/components/confirmar";
import { Aviso, Chip, EsqueletoFilas, ErrorEnLinea } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import type { GoogleMcp, PedidoGoogleMcp, ServicioGoogle } from "@/lib/tipos";

const NIVELES = { core: "Core (lo esencial)", extended: "Extended", complete: "Complete (todas)" };
const CLASE_TEXTO = "min-h-20 w-full rounded-lg border border-input bg-transparent px-2.5 py-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50";

const copiar = (texto: string, aviso: string) => {
  navigator.clipboard.writeText(texto).then(() => toast.success(aviso), () => toast.error("No se pudo copiar"));
};

/** URI a la que Google devuelve el código: la del .env o esta misma página. */
const redireccionDe = (g: GoogleMcp) => g.redirect_uri || (typeof window === "undefined" ? "" : `${window.location.origin}/configuracion/mcp`);

/** 1. Cliente OAuth de Google Cloud: Client ID, Client secret (solo escritura), cuenta y URI de redirección. */
function ClienteOAuth({ g, onCambio }: { g: GoogleMcp; onCambio: (g: GoogleMcp) => void }) {
  const base = { client_id: g.client_id, client_secret: "", cuenta: g.cuenta, redirect_uri: g.redirect_uri };
  const [v, setV] = useState(base);
  const [quitarSecreto, setQuitarSecreto] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const cambios: PedidoGoogleMcp = Object.fromEntries((Object.keys(base) as (keyof typeof base)[])
    .flatMap((k): [string, string][] => (k === "client_secret" ? (quitarSecreto ? [[k, ""]] : v[k] ? [[k, v[k]]] : []) : v[k] !== base[k] ? [[k, v[k]]] : [])));
  const hay = Object.keys(cambios).length > 0;
  const campo = (k: keyof typeof base) => ({ id: k, value: v[k], onChange: (ev: React.ChangeEvent<HTMLInputElement>) => setV((x) => ({ ...x, [k]: ev.target.value })) });

  async function guardar() {
    setGuardando(true);
    setError(null);
    try {
      onCambio(await api.guardarGoogleMcp(cambios));
      setQuitarSecreto(false);
      toast.success("Cliente OAuth guardado en el .env");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setGuardando(false);
    }
  }

  return (
    <form onSubmit={(ev) => { ev.preventDefault(); if (hay) void guardar(); }} className="flex flex-col gap-3">
      <SeccionAjustes titulo="1. Cliente OAuth de Google Cloud"
        descripcion="Credenciales del proyecto de Google Cloud (Credenciales › ID de cliente de OAuth, tipo «Aplicación web»). Se guardan en el .env.">
        <FilaAjuste etiqueta="Client ID"><Input {...campo("client_id")} className="font-mono" placeholder="123…apps.googleusercontent.com" autoComplete="off" /></FilaAjuste>
        <FilaAjuste etiqueta="Client secret">
          <Input {...campo("client_secret")} type="password" autoComplete="off" className="font-mono"
            onChange={(ev) => { setV((x) => ({ ...x, client_secret: ev.target.value })); setQuitarSecreto(false); }}
            placeholder={quitarSecreto ? "Se quitará al guardar" : g.secreto_configurado ? "•••••••• (configurado; escribe para reemplazar)" : "GOCSPX-…"} />
          {g.secreto_configurado && (
            <Button type="button" variant="outline" size="icon" aria-label="Quitar Client secret" aria-pressed={quitarSecreto}
              onClick={() => { setQuitarSecreto((q) => !q); setV((x) => ({ ...x, client_secret: "" })); }}><Trash2 /></Button>
          )}
        </FilaAjuste>
        <FilaAjuste etiqueta="Cuenta de Google">
          <div className="flex w-full flex-col gap-1">
            <Input {...campo("cuenta")} type="email" placeholder="tu.cuenta@empresa.pe" autoComplete="off" />
            <span className="text-xs text-muted-foreground">Se completa sola al autorizar. Los correos y mensajes salen a nombre de esta cuenta.</span>
          </div>
        </FilaAjuste>
        <FilaAjuste etiqueta="URI de redirección">
          <div className="flex w-full flex-col gap-1">
            <div className="flex gap-2">
              <Input {...campo("redirect_uri")} className="font-mono" placeholder={redireccionDe({ ...g, redirect_uri: "" })} autoComplete="off" />
              <Button type="button" variant="outline" size="icon" aria-label="Copiar URI de redirección" onClick={() => copiar(v.redirect_uri || redireccionDe({ ...g, redirect_uri: "" }), "URI copiada")}><Copy /></Button>
            </div>
            <span className="text-xs text-muted-foreground">Regístrala tal cual en «URIs de redireccionamiento autorizados» del cliente OAuth. Vacío = esta página.</span>
          </div>
        </FilaAjuste>
      </SeccionAjustes>
      {error && <ErrorEnLinea titulo="No se guardó" detalle={error} />}
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" disabled={!hay || guardando} onClick={() => { setV(base); setQuitarSecreto(false); setError(null); }}><Undo2 /> Descartar</Button>
        <Button type="submit" disabled={!hay || guardando}><Save /> {guardando ? "Guardando…" : "Guardar"}</Button>
      </div>
    </form>
  );
}

/** 2. Autorización: abre el consentimiento de Google y canjea el código (llega solo por la URL o se pega a mano). */
function Autorizacion({ g, onCambio }: { g: GoogleMcp; onCambio: (g: GoogleMcp) => void }) {
  const [codigo, setCodigo] = useState("");
  const [ocupado, setOcupado] = useState<"autorizar" | "codigo" | "salir" | null>(null);
  const [confirmarSalida, setConfirmarSalida] = useState(false);
  const pendientes = g.servicios.filter((s) => s.falta_consentimiento);

  async function autorizar() {
    setOcupado("autorizar");
    try {
      const r = await api.autorizarGoogle(redireccionDe(g));
      window.open(r.url, "_blank", "noopener");
      toast.info("Se abrió Google en otra pestaña", { description: "Acepta los permisos; luego pega aquí el código o la URL a la que te llevó." });
    } catch (e) {
      toast.error("No se pudo iniciar la autorización", { description: (e as Error).message });
    } finally {
      setOcupado(null);
    }
  }

  async function canjear() {
    setOcupado("codigo");
    try {
      onCambio(await api.codigoGoogle(codigo.trim()));
      setCodigo("");
      toast.success("Cuenta de Google conectada");
    } catch (e) {
      toast.error("No se pudo conectar", { description: (e as Error).message });
    } finally {
      setOcupado(null);
    }
  }

  async function desconectar() {
    setOcupado("salir");
    try {
      onCambio(await api.desconectarGoogle());
      toast.success("Cuenta desconectada", { description: "Se revocó el acceso y se quitó el token del .env." });
    } catch (e) {
      toast.error("No se pudo desconectar", { description: (e as Error).message });
    } finally {
      setOcupado(null);
    }
  }

  const listo = !!g.client_id && g.secreto_configurado;
  return (
    <SeccionAjustes titulo="2. Autorizar la cuenta"
      descripcion="Google pide tu consentimiento y entrega un código. Si vuelve a esta página se conecta solo; si no, copia el código (o la URL completa) y pégalo aquí."
      accion={<Chip tono={g.autorizado ? (pendientes.length ? "aviso" : "exito") : "neutro"}>{g.autorizado ? (pendientes.length ? "faltan permisos" : `conectado${g.cuenta ? ` · ${g.cuenta}` : ""}`) : "sin autorizar"}</Chip>}>
      <div className="flex flex-col gap-3 py-3">
        {!listo && <Aviso>Guarda primero el Client ID y el Client secret.</Aviso>}
        {pendientes.length > 0 && <Aviso>Activaste {pendientes.map((s) => s.nombre).join(", ")} después de autorizar: vuelve a autorizar para darle sus permisos.</Aviso>}
        <div className="flex flex-wrap gap-2">
          <Button type="button" disabled={!listo || !!ocupado} onClick={() => void autorizar()}><ExternalLink /> {g.autorizado ? "Volver a autorizar" : "Autorizar con Google"}</Button>
          {g.autorizado && <Button type="button" variant="outline" disabled={!!ocupado} onClick={() => setConfirmarSalida(true)}><LogOut /> Desconectar</Button>}
        </div>
        <form className="flex flex-col gap-1.5" onSubmit={(ev) => { ev.preventDefault(); if (codigo.trim()) void canjear(); }}>
          <Label htmlFor="codigo-google">Código de autorización</Label>
          <div className="flex gap-2">
            <Input id="codigo-google" value={codigo} onChange={(ev) => setCodigo(ev.target.value)} className="font-mono" autoComplete="off" placeholder="4/0A… o la URL completa con ?code=…" />
            <Button type="submit" variant="secondary" disabled={!codigo.trim() || !!ocupado}><KeyRound /> {ocupado === "codigo" ? "Conectando…" : "Conectar"}</Button>
          </div>
        </form>
      </div>
      <Confirmar abierto={confirmarSalida} onAbierto={setConfirmarSalida} titulo="Desconectar Google" accion="Desconectar" peligro
        descripcion="Se revoca el acceso de la cuenta y se quita el token del .env. El MCP dejará de funcionar hasta que vuelvas a autorizar." onConfirmar={() => { setConfirmarSalida(false); void desconectar(); }} />
    </SeccionAjustes>
  );
}

/** Diálogo de prueba de un servicio. Gmail y Chat envían de verdad: piden destinatario, texto y confirmación. */
function DialogoPrueba({ s, g, onCerrar }: { s: ServicioGoogle | null; g: GoogleMcp; onCerrar: () => void }) {
  const [destinatario, setDestinatario] = useState(s?.id === "gmail" ? g.correo_prueba : "");
  const [texto, setTexto] = useState("");
  const [confirmar, setConfirmar] = useState(false);
  const [probando, setProbando] = useState(false);
  const [resultado, setResultado] = useState<{ ok: boolean; detalle: string } | null>(null);
  if (!s) return null;

  async function probar() {
    setProbando(true);
    setResultado(null);
    try {
      const r = await api.probarGoogle(s!.id, destinatario.trim(), texto.trim());
      setResultado(r);
      if (r.ok) toast.success(`Prueba de ${s!.nombre} correcta`, { description: r.detalle });
      else toast.error(`La prueba de ${s!.nombre} falló`, { description: r.detalle });
    } catch (e) {
      setResultado({ ok: false, detalle: (e as Error).message });
    } finally {
      setProbando(false);
    }
  }

  const ayudas: Record<string, { etiqueta: string; placeholder: string; ayuda: string }> = {
    gmail: { etiqueta: "Enviar a", placeholder: "correo@empresa.pe", ayuda: "Recibe un correo de prueba enviado por Gmail desde tu cuenta." },
    chat: { etiqueta: "Contacto de Google Chat", placeholder: "contacto@empresa.pe o spaces/AAAA…", ayuda: "Mensaje directo a la persona (por su correo) o a un espacio donde estás. No usa el webhook." },
    contacts: { etiqueta: "Buscar", placeholder: "Nombre o correo", ayuda: "Busca en tus contactos y en el directorio de la organización." },
  };
  const campo = ayudas[s.id];
  const falta = s.envia && !destinatario.trim();

  return (
    <Dialog open onOpenChange={(a) => !a && onCerrar()}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>Probar {s.nombre}</DialogTitle>
          <DialogDescription>{campo?.ayuda ?? `Hace una consulta de solo lectura a ${s.nombre} con la cuenta autorizada.`}</DialogDescription>
        </DialogHeader>
        <div className="flex flex-col gap-4">
          {campo && (
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="prueba-destino">{campo.etiqueta}</Label>
              <Input id="prueba-destino" value={destinatario} onChange={(ev) => setDestinatario(ev.target.value)} placeholder={campo.placeholder} autoComplete="off" />
            </div>
          )}
          {s.envia && (
            <div className="flex flex-col gap-1.5">
              <Label htmlFor="prueba-texto">Mensaje (opcional)</Label>
              <textarea id="prueba-texto" value={texto} onChange={(ev) => setTexto(ev.target.value)} rows={3} maxLength={4000} className={CLASE_TEXTO}
                placeholder="Prueba del MCP de Google Workspace desde la web de reportes automatizados." />
            </div>
          )}
          {resultado && <Aviso tono={resultado.ok ? "exito" : "peligro"}>{resultado.detalle}</Aviso>}
        </div>
        <DialogFooter>
          <Button type="button" variant="outline" onClick={onCerrar}>Cerrar</Button>
          <Button type="button" disabled={probando || falta} onClick={() => (s.envia ? setConfirmar(true) : void probar())}>
            <FlaskConical /> {probando ? "Probando…" : s.envia ? "Enviar prueba" : "Probar"}
          </Button>
        </DialogFooter>
        <Confirmar abierto={confirmar} onAbierto={setConfirmar} titulo={`Enviar prueba por ${s.nombre}`} accion="Enviar"
          descripcion={`Se enviará de verdad ${s.id === "gmail" ? "un correo" : "un mensaje"} a ${destinatario.trim()} desde ${g.cuenta || "la cuenta autorizada"}.`}
          onConfirmar={() => { setConfirmar(false); void probar(); }} />
      </DialogContent>
    </Dialog>
  );
}

/** 3. Servicios: cuáles expone el MCP (y qué permisos se piden), solo lectura, nivel y una prueba por servicio. */
function Servicios({ g, onCambio }: { g: GoogleMcp; onCambio: (g: GoogleMcp) => void }) {
  const base = { servicios: g.servicios.filter((s) => s.activo).map((s) => s.id), solo_lectura: g.solo_lectura, nivel: g.nivel };
  const [v, setV] = useState(base);
  const [guardando, setGuardando] = useState(false);
  const [probando, setProbando] = useState<ServicioGoogle | null>(null);
  const hay = JSON.stringify(v) !== JSON.stringify(base);

  async function guardar() {
    setGuardando(true);
    try {
      const nuevo = await api.guardarGoogleMcp(v);
      onCambio(nuevo);
      const faltan = nuevo.servicios.filter((s) => s.falta_consentimiento).length;
      toast.success("Servicios guardados en el .env", { description: faltan ? "Vuelve a autorizar para dar los permisos nuevos." : "El cliente MCP los toma al reiniciarse." });
    } catch (e) {
      toast.error("No se guardó", { description: (e as Error).message });
    } finally {
      setGuardando(false);
    }
  }

  const alternar = (id: string, si: boolean) => setV((x) => ({ ...x, servicios: si ? [...x.servicios, id] : x.servicios.filter((s) => s !== id) }));
  return (
    <div className="flex flex-col gap-3">
      <SeccionAjustes titulo="3. Servicios y pruebas" descripcion="Elige qué puede usar el MCP; cada servicio pide sus permisos al autorizar. «Probar» usa la cuenta ya autorizada.">
        {g.servicios.map((s) => {
          const activo = v.servicios.includes(s.id);
          return (
            <div key={s.id} className="flex flex-wrap items-center gap-3 py-3">
              <Checkbox id={`svc-${s.id}`} checked={activo} onCheckedChange={(x) => alternar(s.id, x === true)} />
              <label htmlFor={`svc-${s.id}`} className="flex min-w-0 flex-1 cursor-pointer flex-col gap-0.5">
                <span className="flex flex-wrap items-center gap-2 text-sm font-medium">
                  {s.nombre}
                  {s.falta_consentimiento ? <Chip tono="aviso">falta autorizar</Chip> : s.activo && g.autorizado ? <Chip tono="exito">listo</Chip> : null}
                  {s.envia && <Chip tono="neutro">envía</Chip>}
                </span>
                <span className="text-xs text-muted-foreground">{s.descripcion}</span>
              </label>
              <Button type="button" variant="outline" size="sm" disabled={!g.autorizado || !s.activo || s.falta_consentimiento} onClick={() => setProbando(s)}
                title={!g.autorizado ? "Autoriza la cuenta primero" : !s.activo ? "Guarda el servicio activo primero" : undefined}><FlaskConical /> Probar</Button>
            </div>
          );
        })}
        <FilaAjuste etiqueta="Solo lectura">
          <div className="flex items-center gap-2">
            <Checkbox id="solo-lectura" checked={v.solo_lectura} onCheckedChange={(x) => setV((y) => ({ ...y, solo_lectura: x === true }))} />
            <label htmlFor="solo-lectura" className="text-sm">El MCP no envía correos ni mensajes (las pruebas de esta página sí).</label>
          </div>
        </FilaAjuste>
        <FilaAjuste etiqueta="Nivel de herramientas (workspace-mcp)">
          <Select value={v.nivel} onValueChange={(n) => setV((y) => ({ ...y, nivel: String(n) }))} items={NIVELES}>
            <SelectTrigger className="w-56"><SelectValue /></SelectTrigger>
            <SelectContent>{Object.entries(NIVELES).map(([k, t]) => <SelectItem key={k} value={k}>{t}</SelectItem>)}</SelectContent>
          </Select>
        </FilaAjuste>
      </SeccionAjustes>
      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" disabled={!hay || guardando} onClick={() => setV(base)}><Undo2 /> Descartar</Button>
        <Button type="button" disabled={!hay || guardando || !v.servicios.length} onClick={() => void guardar()}><Save /> {guardando ? "Guardando…" : "Guardar servicios"}</Button>
      </div>
      {probando && <DialogoPrueba key={probando.id} s={probando} g={g} onCerrar={() => setProbando(null)} />}
    </div>
  );
}

function Bloque({ titulo, json, extra }: { titulo: string; json: unknown; extra?: ReactNode }) {
  const texto = JSON.stringify(json, null, 2);
  return (
    <div className="flex flex-col gap-2 py-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <span className="text-sm font-medium">{titulo}</span>
        <span className="flex flex-wrap gap-2">{extra}<Button type="button" variant="outline" size="sm" onClick={() => copiar(texto, "JSON copiado")}><Copy /> Copiar JSON</Button></span>
      </div>
      <pre className="overflow-x-auto rounded-lg border bg-muted/40 p-3 font-mono text-xs">{texto}</pre>
    </div>
  );
}

/** 4. Conectar el MCP a un cliente (Claude Code, Claude Desktop…): este servidor o el comunitario workspace-mcp. */
function Conexion({ g }: { g: GoogleMcp }) {
  const comando = `claude mcp add google-workspace -- ${g.comando} ${g.args.map((a) => (a.includes(" ") ? `"${a}"` : a)).join(" ")}`;
  return (
    <SeccionAjustes titulo="4. Conectar con tu cliente MCP" descripcion="Pega la configuración en el .mcp.json del cliente. No lleva secretos: el servidor lee credenciales y token del .env.">
      <div className="flex flex-col gap-2 py-3">
        <span className="text-sm font-medium">Herramientas que expone ahora</span>
        {g.herramientas.length ? (
          <ul className="divide-y rounded-lg border">
            {g.herramientas.map((h) => (
              <li key={h.nombre} className="flex flex-col gap-0.5 px-3 py-2">
                <code className="text-sm font-medium">{h.nombre}</code>
                <span className="text-xs text-muted-foreground">{h.descripcion}</span>
              </li>
            ))}
          </ul>
        ) : <span className="text-sm text-muted-foreground">Ninguna: activa algún servicio.</span>}
      </div>
      <Bloque titulo="Este servidor (usa la cuenta autorizada aquí)" json={g.configuracion}
        extra={<Button type="button" variant="outline" size="sm" onClick={() => copiar(comando, "Comando copiado")}><Copy /> Comando de Claude Code</Button>} />
      <Bloque titulo="Alternativa: workspace-mcp (autoriza por su cuenta en http://localhost:8000/oauth2callback)" json={g.configuracion_workspace_mcp} />
      <p className="pb-3 text-xs text-muted-foreground">Usa el Python con el que instalaste el backend (aquí: <code>{g.python}</code>). Reinicia el cliente MCP tras cambiar servicios.</p>
    </SeccionAjustes>
  );
}

/** Al volver de Google con ?code=…&state=… se canjea el código y se limpia la URL. */
function useVueltaDeGoogle(onCambio: (g: GoogleMcp) => void) {
  const params = useSearchParams();
  const router = useRouter();
  const ruta = usePathname();
  const hecho = useRef(false);
  const codigo = params.get("code");
  const state = params.get("state") ?? undefined;
  const error = params.get("error");
  useEffect(() => {
    if (hecho.current || (!codigo && !error)) return;
    hecho.current = true;
    router.replace(ruta, { scroll: false });
    if (error) { toast.error("Google no autorizó", { description: error }); return; }
    api.codigoGoogle(codigo!, state)
      .then((g) => { onCambio(g); toast.success("Cuenta de Google conectada", { description: g.cuenta }); })
      .catch((e: Error) => toast.error("No se pudo conectar", { description: e.message }));
  }, [codigo, state, error, router, ruta, onCambio]);
}

/** MCP de Google Workspace: Gmail y Chat directo a contactos (no el webhook), Contactos, Calendar, Drive, Docs, Sheets, Slides, Forms y Tasks. */
export function PanelMcp() {
  const { datos, error, cargando, recargar } = useConsulta("mcp/google", api.googleMcp);
  const [actual, setActual] = useState<GoogleMcp | null>(null);
  const g = actual ?? datos;
  useVueltaDeGoogle(setActual);
  // Cada vez que cambia la configuración se remontan los formularios con los valores nuevos.
  const version = g ? JSON.stringify([g.client_id, g.secreto_configurado, g.cuenta, g.redirect_uri, g.autorizado, g.servicios.map((s) => [s.activo, s.falta_consentimiento]), g.solo_lectura, g.nivel]) : "";

  return (
    <Pagina>
      <Marco icono={<Plug />} titulo="MCP · Google Workspace"
        descripcion="Conecta tu cuenta de Google para que el asistente envíe correos por Gmail y mensajes de Google Chat a tus contactos, y use Calendar, Drive y más. Todo se guarda en el .env.">
        {error ? <ErrorEnLinea titulo="No se pudo leer el MCP de Google" detalle={`${error} Si acabas de actualizar el sistema, reinicia la API.`} onReintentar={recargar} />
          : cargando && !g ? <EsqueletoFilas filas={6} alto="h-12" />
          : g && (
            <div className="flex flex-col gap-6">
              <Aviso tono="info">
                En Google Cloud: habilita las APIs de Gmail, Google Chat, People, Calendar, Drive, Docs, Sheets, Slides, Forms y Tasks que vayas a usar;
                configura la pantalla de consentimiento y crea un ID de cliente OAuth. Para mensajes de Chat, la API de Google Chat también pide configurar
                una «app de Chat» en el mismo proyecto (basta con nombre y avatar) y una cuenta de Google Workspace.
              </Aviso>
              <ClienteOAuth key={`c-${version}`} g={g} onCambio={setActual} />
              <Autorizacion key={`a-${version}`} g={g} onCambio={setActual} />
              <Servicios key={`s-${version}`} g={g} onCambio={setActual} />
              <Conexion g={g} />
            </div>
          )}
      </Marco>
    </Pagina>
  );
}
