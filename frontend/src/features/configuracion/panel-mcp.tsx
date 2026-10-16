"use client";

import { Copy, ExternalLink, KeyRound, LogOut, Play, Plug, PlugZap, Save, Send, Trash2, Undo2 } from "lucide-react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { toast } from "sonner";
import { FilaAjuste } from "@/components/ajustes";
import { Confirmar } from "@/components/confirmar";
import { Aviso, Chip, EsqueletoFilas, ErrorEnLinea, Punto } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Tarjeta } from "@/components/tarjeta";
import { Terminal } from "@/components/terminal";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import type { GoogleMcp, HerramientaRemota, PedidoGoogleMcp, ServicioGoogle } from "@/lib/tipos";

const CLASE_TEXTO = "w-full rounded-lg border border-input bg-transparent px-2.5 py-2 text-sm outline-none focus-visible:border-ring focus-visible:ring-3 focus-visible:ring-ring/50";
type Cambio = (g: GoogleMcp) => void;

const copiar = (texto: string, aviso = "Copiado") => {
  navigator.clipboard.writeText(texto).then(() => toast.success(aviso), () => toast.error("No se pudo copiar"));
};

/** URI a la que Google devuelve el código: la del .env o esta misma página. */
const redireccionPorDefecto = () => (typeof window === "undefined" ? "" : `${window.location.origin}/configuracion/mcp`);

/** Envuelve una llamada con estado ocupado y toast de error. */
function useAccion() {
  const [ocupado, setOcupado] = useState<string | null>(null);
  const correr = async <T,>(clave: string, fn: () => Promise<T>, error: string): Promise<T | undefined> => {
    setOcupado(clave);
    try {
      return await fn();
    } catch (e) {
      toast.error(error, { description: (e as Error).message });
    } finally {
      setOcupado(null);
    }
  };
  return { ocupado, correr };
}

// ---------------------------------------------------------------- pestaña Cuenta

function Credenciales({ g, onCambio }: { g: GoogleMcp; onCambio: Cambio }) {
  const base = { client_id: g.client_id, client_secret: "", cuenta: g.cuenta, redirect_uri: g.redirect_uri };
  const [v, setV] = useState(base);
  const [quitar, setQuitar] = useState(false);
  const { ocupado, correr } = useAccion();
  const cambios: PedidoGoogleMcp = Object.fromEntries((Object.keys(base) as (keyof typeof base)[])
    .flatMap((k): [string, string][] => (k === "client_secret" ? (quitar ? [[k, ""]] : v[k] ? [[k, v[k]]] : []) : v[k] !== base[k] ? [[k, v[k]]] : [])));
  const hay = Object.keys(cambios).length > 0;
  const campo = (k: keyof typeof base) => ({ id: k, value: v[k], autoComplete: "off", onChange: (ev: React.ChangeEvent<HTMLInputElement>) => { setV((x) => ({ ...x, [k]: ev.target.value })); if (k === "client_secret") setQuitar(false); } });

  async function guardar() {
    const r = await correr("guardar", () => api.guardarGoogleMcp(cambios), "No se guardó");
    if (r) { onCambio(r); toast.success("Credenciales guardadas en el .env"); }
  }

  return (
    <Tarjeta titulo="Cliente OAuth" descripcion="El mismo Client ID y secret para todos los servidores de Google. Se guardan en el .env; el secret no se vuelve a mostrar."
      acciones={<>
        <Button type="button" variant="outline" size="sm" disabled={!hay || !!ocupado} onClick={() => { setV(base); setQuitar(false); }}><Undo2 /> Descartar</Button>
        <Button type="button" size="sm" disabled={!hay || !!ocupado} onClick={() => void guardar()}><Save /> {ocupado ? "Guardando…" : "Guardar"}</Button>
      </>}>
      <div className="divide-y rounded-lg border px-4">
        <FilaAjuste etiqueta="Client ID"><Input {...campo("client_id")} className="font-mono" placeholder="…apps.googleusercontent.com" /></FilaAjuste>
        <FilaAjuste etiqueta="Client secret">
          <Input {...campo("client_secret")} type="password" className="font-mono"
            placeholder={quitar ? "Se quitará al guardar" : g.secreto_configurado ? "•••••••• configurado (escribe para reemplazar)" : "GOCSPX-…"} />
          {g.secreto_configurado && (
            <Button type="button" variant="outline" size="icon" aria-label="Quitar Client secret" aria-pressed={quitar}
              onClick={() => { setQuitar((q) => !q); setV((x) => ({ ...x, client_secret: "" })); }}><Trash2 /></Button>
          )}
        </FilaAjuste>
        <FilaAjuste etiqueta="Cuenta"><Input {...campo("cuenta")} type="email" placeholder="Se completa al autorizar" /></FilaAjuste>
        <FilaAjuste etiqueta="URI de redirección">
          <Input {...campo("redirect_uri")} className="font-mono" placeholder={redireccionPorDefecto()} />
          <Button type="button" variant="outline" size="icon" aria-label="Copiar URI" onClick={() => copiar(v.redirect_uri || redireccionPorDefecto(), "URI copiada")}><Copy /></Button>
        </FilaAjuste>
      </div>
      <p className="text-xs text-muted-foreground">Registra la URI en «URIs de redireccionamiento autorizados» del cliente OAuth (tipo «Aplicación web»). Vacío = esta página.</p>
    </Tarjeta>
  );
}

function Autorizacion({ g, onCambio }: { g: GoogleMcp; onCambio: Cambio }) {
  const [codigo, setCodigo] = useState("");
  const [salir, setSalir] = useState(false);
  const [activos, setActivos] = useState(() => g.servicios.filter((s) => s.activo).map((s) => s.id));
  const { ocupado, correr } = useAccion();
  const pendientes = g.servicios.filter((s) => s.falta_consentimiento);
  const listo = !!g.client_id && g.secreto_configurado;
  const cambioActivos = activos.join() !== g.servicios.filter((s) => s.activo).map((s) => s.id).join();

  async function autorizar() {
    // Primero se guardan los servidores elegidos: de ellos salen los permisos que se piden.
    if (cambioActivos) {
      const guardado = await correr("autorizar", () => api.guardarGoogleMcp({ servicios: activos }), "No se guardaron los servidores");
      if (!guardado) return;
      onCambio(guardado);
    }
    const r = await correr("autorizar", () => api.autorizarGoogle(g.redirect_uri || redireccionPorDefecto()), "No se pudo iniciar la autorización");
    if (r) { window.open(r.url, "_blank", "noopener"); toast.info("Acepta los permisos en Google y pega aquí el código si no vuelve solo."); }
  }

  return (
    <Tarjeta titulo="Autorización"
      descripcion="Elige los servidores y autoriza: Google devuelve un código que se canjea solo al volver a esta página, o lo pegas aquí."
      acciones={<Chip tono={g.autorizado ? (pendientes.length ? "aviso" : "exito") : "neutro"}>{g.autorizado ? (pendientes.length ? "faltan permisos" : `conectado · ${g.cuenta}`) : "sin autorizar"}</Chip>}>
      <div className="flex flex-wrap gap-x-5 gap-y-2">
        {g.servicios.map((s) => (
          <label key={s.id} className="flex cursor-pointer items-center gap-2 text-sm">
            <Checkbox checked={activos.includes(s.id)} onCheckedChange={(x) => setActivos((a) => (x === true ? [...a, s.id] : a.filter((i) => i !== s.id)))} />
            {s.nombre}
          </label>
        ))}
      </div>
      {!listo && <Aviso>Guarda primero el Client ID y el Client secret.</Aviso>}
      {g.autorizado && (cambioActivos || pendientes.length > 0) && (
        <Aviso>{cambioActivos ? "Cambiaste los servidores" : `Faltan los permisos de ${pendientes.map((s) => s.nombre).join(", ")}`}: vuelve a autorizar.</Aviso>
      )}
      <div className="flex flex-wrap gap-2">
        <Button type="button" disabled={!listo || !!ocupado || !activos.length} onClick={() => void autorizar()}><ExternalLink /> {g.autorizado ? "Volver a autorizar" : "Autorizar con Google"}</Button>
        {g.autorizado && <Button type="button" variant="outline" disabled={!!ocupado} onClick={() => setSalir(true)}><LogOut /> Desconectar</Button>}
      </div>
      <form className="flex gap-2" onSubmit={(ev) => {
        ev.preventDefault();
        void correr("codigo", () => api.codigoGoogle(codigo.trim()), "No se pudo conectar").then((r) => { if (r) { onCambio(r); setCodigo(""); toast.success("Cuenta conectada", { description: r.cuenta }); } });
      }}>
        <Input value={codigo} onChange={(ev) => setCodigo(ev.target.value)} className="font-mono" autoComplete="off" aria-label="Código de autorización" placeholder="Código 4/0A… o la URL completa con ?code=…" />
        <Button type="submit" variant="secondary" disabled={!codigo.trim() || !!ocupado}><KeyRound /> Conectar</Button>
      </form>
      <Confirmar abierto={salir} onAbierto={setSalir} titulo="Desconectar Google" accion="Desconectar" peligro
        descripcion="Se revoca el acceso y se quita el token del .env." onConfirmar={() => {
          setSalir(false);
          void correr("salir", api.desconectarGoogle, "No se pudo desconectar").then((r) => r && onCambio(r));
        }} />
    </Tarjeta>
  );
}

// ---------------------------------------------------------------- pestaña de cada servidor

/** Argumentos de ejemplo a partir del esquema: las propiedades requeridas, vacías. */
const plantilla = (h: HerramientaRemota) =>
  JSON.stringify(Object.fromEntries((h.esquema.required ?? []).map((k) => [k, h.esquema.properties?.[k]?.type === "number" || h.esquema.properties?.[k]?.type === "integer" ? 0 : ""])), null, 2);

function ProbarMcp({ s }: { s: ServicioGoogle }) {
  const [herramientas, setHerramientas] = useState<HerramientaRemota[] | null>(null);
  const [elegida, setElegida] = useState<HerramientaRemota | null>(null);
  const [args, setArgs] = useState("{}");
  const [salida, setSalida] = useState("");
  const { ocupado, correr } = useAccion();

  async function conectar() {
    const r = await correr("conectar", () => api.herramientasGoogle(s.id), "No se pudo probar");
    if (!r) return;
    setHerramientas(r.ok ? r.herramientas : null);
    setSalida(`${r.ok ? "✓" : "✗"} ${r.detalle}`);
  }

  async function ejecutar() {
    let argumentos: Record<string, unknown>;
    try {
      argumentos = JSON.parse(args || "{}");
    } catch {
      toast.error("Los argumentos no son un JSON válido");
      return;
    }
    const r = await correr("ejecutar", () => api.ejecutarGoogle(s.id, elegida!.nombre, argumentos), "No se pudo ejecutar");
    if (r) setSalida(`${r.ok ? "✓" : "✗"} ${elegida!.nombre}\n${r.detalle}`);
  }

  return (
    <Tarjeta titulo="Probar MCP" descripcion="Se conecta al servidor de Google con tu cuenta, lista sus herramientas y puedes ejecutar una."
      acciones={<Button size="sm" disabled={!!ocupado} onClick={() => void conectar()}><PlugZap className={ocupado === "conectar" ? "animate-pulse" : ""} /> {ocupado === "conectar" ? "Conectando…" : "Probar conexión"}</Button>}>
      {herramientas && (
        <div className="grid gap-3 lg:grid-cols-[minmax(0,18rem)_1fr]">
          <ul className="max-h-80 divide-y overflow-y-auto rounded-lg border">
            {herramientas.map((h) => (
              <li key={h.nombre}>
                <button type="button" onClick={() => { setElegida(h); setArgs(plantilla(h)); }}
                  className={`flex w-full flex-col gap-0.5 px-3 py-2 text-left transition-colors hover:bg-muted/40 ${elegida?.nombre === h.nombre ? "bg-muted" : ""}`}>
                  <code className="text-sm font-medium">{h.nombre}</code>
                  <span className="line-clamp-2 text-xs text-muted-foreground">{h.descripcion}</span>
                </button>
              </li>
            ))}
          </ul>
          {elegida ? (
            <div className="flex flex-col gap-2">
              <span className="text-sm"><code className="font-medium">{elegida.nombre}</code> · argumentos (JSON)</span>
              <textarea value={args} onChange={(ev) => setArgs(ev.target.value)} rows={6} spellCheck={false} className={`${CLASE_TEXTO} font-mono text-xs`} aria-label="Argumentos" />
              {elegida.esquema.properties && (
                <span className="text-xs text-muted-foreground">
                  {Object.entries(elegida.esquema.properties).map(([k, p]) => `${k}${elegida.esquema.required?.includes(k) ? "*" : ""}${p.type ? `: ${p.type}` : ""}`).join(" · ")}
                </span>
              )}
              <div className="flex justify-end"><Button size="sm" disabled={!!ocupado} onClick={() => void ejecutar()}><Play /> {ocupado === "ejecutar" ? "Ejecutando…" : "Ejecutar"}</Button></div>
            </div>
          ) : <span className="text-sm text-muted-foreground">Elige una herramienta para ejecutarla.</span>}
        </div>
      )}
      {salida && <Terminal titulo={s.url} texto={salida} />}
    </Tarjeta>
  );
}

function EnvioDirecto({ s, g }: { s: ServicioGoogle; g: GoogleMcp }) {
  const [para, setPara] = useState(s.id === "gmail" ? g.correo_prueba : "");
  const [texto, setTexto] = useState("");
  const [confirmar, setConfirmar] = useState(false);
  const { ocupado, correr } = useAccion();
  const esChat = s.id === "chat";

  return (
    <Tarjeta titulo={esChat ? "Mensaje a un contacto" : "Enviar correo"}
      descripcion={esChat ? "Mensaje directo como tu cuenta (no por el webhook). Lo usa el servidor propio «google-envio»."
        : "El MCP de Gmail de Google solo crea borradores; el envío lo hace el servidor propio «google-envio»."}>
      <div className="flex flex-col gap-2">
        <Input value={para} onChange={(ev) => setPara(ev.target.value)} autoComplete="off" aria-label="Destinatario" placeholder={esChat ? "contacto@empresa.pe o spaces/AAAA…" : "correo@empresa.pe"} />
        <textarea value={texto} onChange={(ev) => setTexto(ev.target.value)} rows={3} maxLength={4000} className={CLASE_TEXTO} aria-label="Mensaje" placeholder="Prueba desde la web de reportes automatizados." />
        <div className="flex justify-end">
          <Button size="sm" disabled={!para.trim() || !!ocupado} onClick={() => setConfirmar(true)}><Send /> {ocupado ? "Enviando…" : "Enviar"}</Button>
        </div>
      </div>
      <Confirmar abierto={confirmar} onAbierto={setConfirmar} titulo={esChat ? "Enviar mensaje de Chat" : "Enviar correo"} accion="Enviar"
        descripcion={`Se enviará de verdad a ${para.trim()} desde ${g.cuenta || "la cuenta autorizada"}.`}
        onConfirmar={() => {
          setConfirmar(false);
          void correr("enviar", () => api.enviarGoogle(s.id, para.trim(), texto.trim()), "No se pudo enviar").then((r) => {
            if (!r) return;
            if (r.ok) toast.success(r.detalle); else toast.error("No se envió", { description: r.detalle });
          });
        }} />
    </Tarjeta>
  );
}

function PestanaServidor({ s, g }: { s: ServicioGoogle; g: GoogleMcp }) {
  const bloqueo = !g.autorizado ? "Autoriza la cuenta en la pestaña Cuenta." : !s.activo ? `${s.nombre} no está activo: márcalo en Cuenta y vuelve a autorizar.`
    : s.falta_consentimiento ? "Faltan los permisos de este servidor: vuelve a autorizar en Cuenta." : null;
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-wrap items-center gap-2 text-sm">
        <code className="rounded bg-muted px-2 py-1 text-xs">{s.url}</code>
        <Button variant="ghost" size="icon-sm" aria-label="Copiar URL" onClick={() => copiar(s.url, "URL copiada")}><Copy /></Button>
        <span className="text-xs text-muted-foreground" title={s.scopes.join("\n")}>{s.scopes.length} permisos: {s.scopes.map((x) => x.split("/").pop()).join(", ")}</span>
      </div>
      {bloqueo ? <Aviso>{bloqueo}</Aviso> : (
        <>
          <ProbarMcp key={s.id} s={s} />
          {s.envia && <EnvioDirecto s={s} g={g} />}
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------- pestaña Conectar

function Conectar({ g }: { g: GoogleMcp }) {
  const json = JSON.stringify(g.configuracion, null, 2);
  return (
    <Tarjeta titulo="Configuración del cliente MCP" descripcion="Pégala en el .mcp.json (o la configuración MCP) de tu cliente."
      acciones={<Button size="sm" variant="outline" onClick={() => copiar(json, "JSON copiado")}><Copy /> Copiar JSON</Button>}>
      <Aviso tono="info">Reemplaza <code>{"<GOOGLE_OAUTH_CLIENT_SECRET del .env>"}</code> por tu Client secret: la web nunca lo muestra. «google-envio» es el servidor propio que envía correos y mensajes de Chat; corre con <code>{g.python}</code>.</Aviso>
      <pre className="overflow-x-auto rounded-lg border bg-muted/40 p-3 font-mono text-xs">{json}</pre>
      {g.herramientas_envio.length > 0 && (
        <span className="text-xs text-muted-foreground">google-envio: {g.herramientas_envio.map((h) => h.nombre).join(", ")}</span>
      )}
    </Tarjeta>
  );
}

// ---------------------------------------------------------------- página

/** Al volver de Google con ?code=…&state=… se canjea el código y se limpia la URL. */
function useVueltaDeGoogle(onCambio: Cambio) {
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

/** MCP de Google Workspace por pestañas (como el detalle de un reporte): Cuenta, un servidor oficial por pestaña y Conectar. */
export function PanelMcp() {
  const { datos, error, cargando, recargar } = useConsulta("mcp/google", api.googleMcp);
  const [actual, setActual] = useState<GoogleMcp | null>(null);
  const g = actual ?? datos;
  useVueltaDeGoogle(setActual);
  const params = useSearchParams();
  const router = useRouter();
  const ruta = usePathname();
  const pestanas = ["cuenta", ...(g?.servicios.map((s) => s.id) ?? []), "conectar"];
  const pedida = params.get("tab");
  const pestana = pedida && pestanas.includes(pedida) ? pedida : "cuenta";
  const irA = (p: string) => router.replace(p === "cuenta" ? ruta : `${ruta}?tab=${p}`, { scroll: false });
  // Los formularios se remontan cuando cambia lo guardado, para partir de los valores nuevos.
  const version = g ? JSON.stringify([g.client_id, g.secreto_configurado, g.cuenta, g.redirect_uri, g.autorizado, g.servicios.map((s) => s.activo)]) : "";

  return (
    <Pagina>
      <Marco icono={<Plug />} titulo="MCP · Google Workspace" descripcion="Servidores MCP oficiales de Google con tu cuenta, y envío por Gmail y Chat.">
        {error ? <ErrorEnLinea titulo="No se pudo leer el MCP de Google" detalle={`${error} Si acabas de actualizar el sistema, reinicia la API.`} onReintentar={recargar} />
          : cargando && !g ? <EsqueletoFilas filas={4} alto="h-12" />
          : g && (
            <Tabs value={pestana} onValueChange={(v) => irA(String(v))}>
              <TabsList className="w-full justify-start overflow-x-auto no-scrollbar sm:w-fit">
                <TabsTrigger value="cuenta">Cuenta</TabsTrigger>
                {g.servicios.map((s) => (
                  <TabsTrigger key={s.id} value={s.id} className="gap-1.5">
                    {s.nombre}
                    <Punto tono={!s.activo ? "neutro" : !g.autorizado || s.falta_consentimiento ? "aviso" : "exito"}
                      etiqueta={!s.activo ? "inactivo" : !g.autorizado || s.falta_consentimiento ? "falta autorizar" : "listo"} />
                  </TabsTrigger>
                ))}
                <TabsTrigger value="conectar">Conectar</TabsTrigger>
              </TabsList>
              <TabsContent value="cuenta" className="flex flex-col gap-4 pt-3">
                <Credenciales key={`c-${version}`} g={g} onCambio={setActual} />
                <Autorizacion key={`a-${version}`} g={g} onCambio={setActual} />
              </TabsContent>
              {g.servicios.map((s) => (
                <TabsContent key={s.id} value={s.id} className="pt-3"><PestanaServidor s={s} g={g} /></TabsContent>
              ))}
              <TabsContent value="conectar" className="pt-3"><Conectar g={g} /></TabsContent>
            </Tabs>
          )}
      </Marco>
    </Pagina>
  );
}
