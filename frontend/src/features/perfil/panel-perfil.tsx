"use client";

import { Copy, Database, KeyRound, Monitor, Moon, PlugZap, SlidersHorizontal, Sun, UserRound } from "lucide-react";
import { useRouter, useSearchParams } from "next/navigation";
import { useTheme } from "next-themes";
import { useState } from "react";
import { toast } from "sonner";
import { Chip, EsqueletoFilas, ErrorEnLinea } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { fecha, iniciales } from "@/lib/formato";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import type { PruebaConexion, Servidor } from "@/lib/tipos";

function TarjetaServidor({ s, probando, ultima, onProbar }: { s: Servidor; probando: boolean; ultima?: PruebaConexion; onProbar: () => void }) {
  return (
    <div className="flex flex-col gap-3 rounded-lg border bg-card p-4">
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 flex-col gap-1">
          <div className="flex items-center gap-2">
            <Database className="size-4 text-muted-foreground" />
            <span className="font-medium">{s.nombre}</span>
            {ultima && <Chip tono={ultima.ok ? "exito" : "peligro"}>{ultima.ok ? `OK · ${ultima.milisegundos} ms` : "Falla"}</Chip>}
          </div>
          <span className="font-mono text-xs text-muted-foreground">{s.servidor}</span>
        </div>
        <Button variant="outline" size="sm" onClick={onProbar} disabled={probando}>
          <PlugZap className={probando ? "animate-pulse" : ""} /> {probando ? "Probando…" : "Test de conexión"}
        </Button>
      </div>
      <dl className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
        <dt className="text-muted-foreground">Autenticación</dt>
        <dd className="flex items-center gap-1.5">
          {s.autenticacion}
          {s.autenticacion === "SQL" && (
            <Chip tono={s.credenciales_en_env ? "exito" : "aviso"}><KeyRound className="size-3" />{s.credenciales_en_env ? "credenciales en .env" : "faltan en .env"}</Chip>
          )}
        </dd>
        <dt className="text-muted-foreground">Bases</dt>
        <dd className="text-muted-foreground">{s.bases.slice(0, 8).join(", ")}{s.bases.length > 8 && ` y ${s.bases.length - 8} más`}</dd>
      </dl>
      {ultima && !ultima.ok && <p className="font-mono text-xs break-all text-[var(--mis-danger)]">{ultima.detalle}</p>}
    </div>
  );
}

function BasesDeDatos() {
  const { datos, error, cargando, recargar } = useConsulta("servidores", api.servidores);
  const [probando, setProbando] = useState<Set<string>>(new Set());
  const [resultados, setResultados] = useState<Record<string, PruebaConexion>>({});

  async function probar(s: Servidor) {
    setProbando((p) => new Set(p).add(s.nombre));
    try {
      const r = await api.probarServidor(s.nombre);
      setResultados((x) => ({ ...x, [s.nombre]: r }));
      if (r.ok) toast.success(`${s.nombre}: conexión correcta`, { description: `${s.servidor} · ${r.milisegundos} ms` });
      else toast.error(`${s.nombre}: sin conexión`, { description: r.detalle });
    } catch (e) {
      toast.error("No se pudo probar la conexión", { description: (e as Error).message });
    } finally {
      setProbando((p) => { const n = new Set(p); n.delete(s.nombre); return n; });
    }
  }

  if (error) return <ErrorEnLinea titulo="No se pudieron leer los servidores" detalle={error} onReintentar={recargar} />;
  if (cargando && !datos) return <EsqueletoFilas filas={3} alto="h-32" />;
  return (
    <div className="flex flex-col gap-4">
      <Encabezado titulo="Bases de datos" descripcion="Las 3 conexiones de SQL Server. Las credenciales viven solo en el .env de la API; aquí no se muestran ni se editan."
        accion={<Button size="sm" disabled={probando.size > 0} onClick={() => datos?.forEach(probar)}><PlugZap /> Probar todas</Button>} />
      <div className="grid gap-3 xl:grid-cols-3">
        {datos?.map((s) => <TarjetaServidor key={s.nombre} s={s} probando={probando.has(s.nombre)} ultima={resultados[s.nombre]} onProbar={() => probar(s)} />)}
      </div>
    </div>
  );
}

function Encabezado({ titulo, descripcion, accion }: { titulo: string; descripcion: string; accion?: React.ReactNode }) {
  return (
    <div className="flex flex-wrap items-start justify-between gap-3">
      <div>
        <h2 className="text-base font-semibold">{titulo}</h2>
        <p className="text-sm text-muted-foreground">{descripcion}</p>
      </div>
      {accion}
    </div>
  );
}

function Fila({ etiqueta, valor, ayuda, copiable }: { etiqueta: string; valor: string; ayuda?: string; copiable?: boolean }) {
  return (
    <div className="flex flex-col gap-1 py-3 sm:flex-row sm:items-center sm:gap-6">
      <span className="w-56 shrink-0 text-sm text-muted-foreground">{etiqueta}</span>
      <div className="flex min-w-0 flex-1 items-center gap-2">
        <div className="flex min-w-0 flex-col">
          <span className="truncate font-mono text-sm">{valor}</span>
          {ayuda && <span className="text-xs text-muted-foreground">{ayuda}</span>}
        </div>
        {copiable && (
          <Button variant="ghost" size="icon-sm" aria-label={`Copiar ${etiqueta}`} className="ml-auto"
            onClick={() => { navigator.clipboard.writeText(valor); toast.success("Copiado"); }}><Copy /></Button>
        )}
      </div>
    </div>
  );
}

function General() {
  const { datos: c, error, cargando, recargar } = useConsulta("configuracion", api.configuracion);
  if (error) return <ErrorEnLinea titulo="No se pudo leer la configuración" detalle={error} onReintentar={recargar} />;
  if (cargando && !c) return <EsqueletoFilas filas={5} />;
  if (!c) return null;
  return (
    <div className="flex flex-col gap-4">
      <Encabezado titulo="General" descripcion="Lo que la API leyó del .env al arrancar. Para cambiarlo, edita el .env y reinicia la API." />
      <div className="divide-y rounded-lg border px-4">
        <Fila etiqueta="Fecha de corte mensual" valor={c.corte_mensual.fecha ? fecha(c.corte_mensual.fecha) : "Sin definir"} ayuda={c.corte_mensual.origen} />
        <Fila etiqueta="Fecha de corte diaria" valor={c.corte_diario.fecha ? fecha(c.corte_diario.fecha) : "Sin definir"} ayuda={c.corte_diario.origen} />
        <Fila etiqueta="Carpeta de entradas" valor={c.dir_inputs} copiable />
        <Fila etiqueta="Carpeta de salidas" valor={c.dir_outputs} copiable />
        <Fila etiqueta="Driver ODBC" valor={c.driver_odbc} />
      </div>
    </div>
  );
}

function Cuenta() {
  const { datos: p, error, cargando, recargar } = useConsulta("perfil", api.perfil);
  const { resolvedTheme, setTheme } = useTheme();
  if (error) return <ErrorEnLinea titulo="No se pudo leer el perfil" detalle={error} onReintentar={recargar} />;
  if (cargando && !p) return <EsqueletoFilas filas={5} />;
  if (!p) return null;
  const si = (ok: boolean, texto: string) => <Chip tono={ok ? "exito" : "aviso"}>{texto}</Chip>;
  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center gap-4">
        <span className="flex size-14 items-center justify-center rounded-xl bg-primary text-lg font-semibold text-primary-foreground">{iniciales(p.usuario)}</span>
        <div className="flex flex-col">
          <span className="text-lg font-semibold">{p.usuario}</span>
          <span className="text-sm text-muted-foreground">Ejecuta la API en {p.equipo}</span>
        </div>
      </div>
      <div className="flex flex-col gap-4">
        <Encabezado titulo="Correo" descripcion="Cuenta con que se envía el resumen diario y a quién llega la prueba. Se configura en el .env." />
        <div className="divide-y rounded-lg border px-4">
          <Fila etiqueta="Correo de prueba" valor={p.correo_prueba} ayuda="Recibe la prueba antes de enviar a toda la lista" copiable />
          <Fila etiqueta="Cuenta de envío" valor={p.cuenta_envio ?? "Sin definir (SMTP_USER)"} />
          <div className="flex flex-wrap items-center gap-2 py-3 text-sm">
            <span className="w-56 shrink-0 text-muted-foreground">Estado</span>
            {si(p.clave_envio_configurada, p.clave_envio_configurada ? "contraseña configurada" : "falta SMTP_PASSWORD")}
            {si(p.webhook_configurado, p.webhook_configurado ? "aviso a Google Chat" : "sin webhook de Google Chat")}
            {si(p.destinatarios !== null, p.destinatarios !== null ? `${p.destinatarios} destinatarios` : "no se pudo leer la lista")}
          </div>
        </div>
      </div>
      <div className="flex flex-col gap-4">
        <Encabezado titulo="Apariencia" descripcion="Se guarda en este navegador." />
        <div className="flex gap-2">
          <Button variant={resolvedTheme === "dark" ? "outline" : "default"} size="sm" onClick={() => setTheme("light")}><Sun /> Claro</Button>
          <Button variant={resolvedTheme === "dark" ? "default" : "outline"} size="sm" onClick={() => setTheme("dark")}><Moon /> Oscuro</Button>
          <Button variant="ghost" size="sm" onClick={() => setTheme("system")}><Monitor /> Como el sistema</Button>
        </div>
      </div>
    </div>
  );
}

const SECCIONES = {
  cuenta: { texto: "Perfil", icono: UserRound },
  general: { texto: "Configuración", icono: SlidersHorizontal },
  bases: { texto: "Bases de datos", icono: Database },
} as const;
type Seccion = keyof typeof SECCIONES;

/** Perfil (como el de Dokploy): cuenta y, en secciones, la configuración; la sección va en la URL. */
export function PanelPerfil() {
  const params = useSearchParams();
  const router = useRouter();
  const pedida = params.get("seccion") as Seccion | null;
  const seccion: Seccion = pedida && pedida in SECCIONES ? pedida : "cuenta";
  return (
    <Pagina>
      <Marco icono={<UserRound />} titulo="Perfil" descripcion="Tu cuenta, la configuración de la API y las conexiones a las bases de datos.">
        <Tabs value={seccion} onValueChange={(v) => router.replace(v === "cuenta" ? "/perfil" : `/perfil?seccion=${v}`, { scroll: false })} orientation="vertical" className="gap-6 md:flex-row">
          <TabsList variant="line" className="h-fit w-full flex-row items-stretch md:w-48 md:flex-col">
            {(Object.keys(SECCIONES) as Seccion[]).map((s) => {
              const { texto, icono: Icono } = SECCIONES[s];
              return <TabsTrigger key={s} value={s} className="justify-start"><Icono /> {texto}</TabsTrigger>;
            })}
          </TabsList>
          <TabsContent value="cuenta" className="min-w-0"><Cuenta /></TabsContent>
          <TabsContent value="general" className="min-w-0"><General /></TabsContent>
          <TabsContent value="bases" className="min-w-0"><BasesDeDatos /></TabsContent>
        </Tabs>
      </Marco>
    </Pagina>
  );
}
