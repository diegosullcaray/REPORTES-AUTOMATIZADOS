"use client";

import { Bot, PenBox, Plug, Plus, Trash2 } from "lucide-react";
import { useState, type ReactNode } from "react";
import { toast } from "sonner";
import { Confirmar } from "@/components/confirmar";
import { Chip, EsqueletoFilas, EstadoVacio, ErrorEnLinea } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Button } from "@/components/ui/button";
import { Checkbox } from "@/components/ui/checkbox";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { Field, FieldDescription, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useConsulta } from "@/hooks/use-consulta";
import { api } from "@/lib/api";
import type { ConfigIA } from "@/lib/tipos";

/** Proveedores conocidos: rellenan la API URL (el proveedor se deduce de la URL, como en Dokploy). */
const PROVEEDORES = [
  { nombre: "OpenAI", url: "https://api.openai.com/v1" },
  { nombre: "Anthropic", url: "https://api.anthropic.com/v1" },
  { nombre: "Google Gemini", url: "https://generativelanguage.googleapis.com/v1beta/openai" },
  { nombre: "Mistral", url: "https://api.mistral.ai/v1" },
  { nombre: "OpenRouter", url: "https://openrouter.ai/api/v1" },
  { nombre: "DeepInfra", url: "https://api.deepinfra.com/v1/openai" },
  { nombre: "Ollama (local)", url: "http://localhost:11434" },
] as const;

function Campo({ id, etiqueta, ayuda, children }: { id: string; etiqueta: string; ayuda?: string; children: ReactNode }) {
  return (
    <Field>
      <FieldLabel htmlFor={id}>{etiqueta}</FieldLabel>
      {children}
      {ayuda && <FieldDescription>{ayuda}</FieldDescription>}
    </Field>
  );
}

/** Alta o edición de una conexión. La API key es de solo escritura: al editar, vacía = conservar la guardada. */
function DialogoIA({ actual, onCerrar, onGuardado }: { actual: ConfigIA | null; onCerrar: () => void; onGuardado: () => void }) {
  const [v, setV] = useState({ nombre: actual?.nombre ?? "", api_url: actual?.api_url ?? "", api_key: "", modelo: actual?.modelo ?? "", activo: actual?.activo ?? true });
  const [modelos, setModelos] = useState<string[]>([]);
  const [ocupado, setOcupado] = useState<"guardar" | "modelos" | null>(null);
  const campo = (k: "nombre" | "api_url" | "api_key" | "modelo") => ({ id: `ia-${k}`, value: v[k], autoComplete: "off", onChange: (ev: React.ChangeEvent<HTMLInputElement>) => setV((x) => ({ ...x, [k]: ev.target.value })) });

  async function cargarModelos() {
    setOcupado("modelos");
    try {
      const r = await api.modelosIA({ api_url: v.api_url, api_key: v.api_key, id: actual?.id });
      setModelos(r.modelos);
      toast.success(`${r.modelos.length} modelos disponibles`);
      if (!v.modelo && r.modelos[0]) setV((x) => ({ ...x, modelo: r.modelos[0] }));
    } catch (e) {
      toast.error("No se pudieron cargar los modelos", { description: (e as Error).message });
    } finally {
      setOcupado(null);
    }
  }

  async function guardar() {
    setOcupado("guardar");
    try {
      await (actual ? api.actualizarIA(actual.id, v) : api.crearIA(v));
      toast.success("Conexión guardada en el .env");
      onGuardado();
      onCerrar();
    } catch (e) {
      toast.error("No se guardó", { description: (e as Error).message });
      setOcupado(null);
    }
  }

  return (
    <Dialog open onOpenChange={(a) => !a && onCerrar()}>
      <DialogContent className="sm:max-w-lg">
        <DialogHeader>
          <DialogTitle>{actual ? `Editar ${actual.nombre}` : "Conectar un proveedor de IA"}</DialogTitle>
          <DialogDescription>Conexión por API key. Se guarda en el .env y la clave no se vuelve a mostrar.</DialogDescription>
        </DialogHeader>
        <form id="form-ia" onSubmit={(ev) => { ev.preventDefault(); void guardar(); }}>
          <FieldGroup>
          <Campo id="ia-nombre" etiqueta="Nombre"><Input {...campo("nombre")} required maxLength={60} placeholder="OpenAI producción" /></Campo>
          <Campo id="ia-proveedor" etiqueta="Proveedor" ayuda="Rellena la API URL; puedes escribir cualquier endpoint compatible con OpenAI.">
            <Select value="" onValueChange={(nombre: string | null) => { const p = PROVEEDORES.find((x) => x.nombre === nombre); if (p) { setV((x) => ({ ...x, api_url: p.url })); setModelos([]); } }}>
              <SelectTrigger id="ia-proveedor" className="w-full"><SelectValue placeholder="Elegir para rellenar la URL…" /></SelectTrigger>
              <SelectContent>{PROVEEDORES.map((p) => <SelectItem key={p.nombre} value={p.nombre}>{p.nombre}</SelectItem>)}</SelectContent>
            </Select>
          </Campo>
          <Campo id="ia-api_url" etiqueta="API URL"><Input {...campo("api_url")} required type="url" className="font-mono" placeholder="https://api.openai.com/v1" /></Campo>
          <Campo id="ia-api_key" etiqueta="API key" ayuda={actual?.clave_configurada ? "Configurada: déjala vacía para conservarla." : "Ollama local no la necesita."}>
            <Input {...campo("api_key")} type="password" className="font-mono" placeholder={actual?.clave_configurada ? "•••••••• (escribe para reemplazar)" : "sk-…"} />
          </Campo>
          <Campo id="ia-modelo" etiqueta="Modelo">
            <div className="flex gap-2">
              <Input {...campo("modelo")} required list="ia-modelos" placeholder="gpt-4o-mini" className="font-mono" />
              <Button type="button" variant="outline" disabled={!v.api_url || !!ocupado} onClick={() => void cargarModelos()}>{ocupado === "modelos" ? "Cargando…" : "Cargar modelos"}</Button>
            </div>
            <datalist id="ia-modelos">{modelos.map((m) => <option key={m} value={m} />)}</datalist>
          </Campo>
          <label className="flex cursor-pointer items-center gap-2 text-sm">
            <Checkbox checked={v.activo} onCheckedChange={(c) => setV((x) => ({ ...x, activo: c === true }))} /> Habilitada
          </label>
          </FieldGroup>
        </form>
        <DialogFooter>
          <Button type="submit" form="form-ia" disabled={!!ocupado}>{ocupado === "guardar" ? "Guardando…" : "Guardar"}</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

function Fila({ c, onEditar, onEliminar, onCambio }: { c: ConfigIA; onEditar: () => void; onEliminar: () => void; onCambio: () => void }) {
  const [probando, setProbando] = useState(false);
  async function probar() {
    setProbando(true);
    try {
      const r = await api.probarIA(c.id);
      toast.success("Conexión correcta", { description: `${r.modelos.length} modelos disponibles${r.modelos.includes(c.modelo) || !r.modelos.length ? "" : ` · «${c.modelo}» no figura en la lista`}` });
    } catch (e) {
      toast.error("La conexión falló", { description: (e as Error).message });
    } finally {
      setProbando(false);
      onCambio();
    }
  }
  return (
    <div className="flex flex-wrap items-center gap-3 rounded-lg border p-4">
      <span className="flex size-10 shrink-0 items-center justify-center rounded-lg border bg-muted text-muted-foreground"><Bot className="size-5" /></span>
      <div className="flex min-w-0 flex-1 flex-col gap-0.5">
        <span className="flex flex-wrap items-center gap-2 font-medium">
          {c.nombre}
          <Chip tono="info">{c.proveedor}</Chip>
          <Chip tono={c.activo ? "exito" : "neutro"}>{c.activo ? "habilitada" : "deshabilitada"}</Chip>
          {!c.clave_configurada && c.proveedor !== "ollama" && <Chip tono="aviso">sin API key</Chip>}
        </span>
        <span className="truncate font-mono text-xs text-muted-foreground" title={c.api_url}>{c.modelo} · {c.api_url}</span>
      </div>
      <div className="flex gap-2">
        <Button variant="secondary" size="sm" disabled={probando} onClick={() => void probar()}><Plug /> {probando ? "Probando…" : "Probar"}</Button>
        <Button variant="outline" size="sm" onClick={onEditar}><PenBox /> Editar</Button>
        <Button variant="outline" size="icon-sm" aria-label={`Eliminar ${c.nombre}`} onClick={onEliminar}><Trash2 /></Button>
      </div>
    </div>
  );
}

/** Inteligencia artificial (página «AI» de Settings en Dokploy): conexiones por API key con probar, editar y eliminar. */
export function PanelIA() {
  const { datos, error, cargando, recargar } = useConsulta("ia", api.ia);
  const [editando, setEditando] = useState<ConfigIA | "nueva" | null>(null);
  const [borrando, setBorrando] = useState<ConfigIA | null>(null);

  async function eliminar(c: ConfigIA) {
    try {
      await api.eliminarIA(c.id);
      toast.success(`Se eliminó ${c.nombre}`);
      recargar();
    } catch (e) {
      toast.error("No se pudo eliminar", { description: (e as Error).message });
    }
  }

  return (
    <Pagina>
      <Marco icono={<Bot />} titulo="Inteligencia artificial" descripcion="Conecta proveedores de IA con su API key. Se guardan en el .env; la clave no se vuelve a mostrar."
        acciones={datos && <Button size="sm" onClick={() => setEditando("nueva")}><Plus /> Conectar IA</Button>}>
        {error ? <ErrorEnLinea titulo="No se pudieron leer las conexiones" detalle={`${error} Si acabas de actualizar el sistema, reinicia la API.`} onReintentar={recargar} />
          : cargando && !datos ? <EsqueletoFilas filas={2} alto="h-16" />
          : datos && (datos.length === 0
            ? <EstadoVacio titulo="Sin conexiones de IA" descripcion="Conecta OpenAI, Anthropic, Gemini, Mistral, OpenRouter u Ollama con su API key." />
            : <div className="flex flex-col gap-3">{datos.map((c) => <Fila key={c.id} c={c} onEditar={() => setEditando(c)} onEliminar={() => setBorrando(c)} onCambio={recargar} />)}</div>)}
      </Marco>
      {editando && <DialogoIA key={editando === "nueva" ? "nueva" : editando.id} actual={editando === "nueva" ? null : editando} onCerrar={() => setEditando(null)} onGuardado={recargar} />}
      <Confirmar abierto={!!borrando} onAbierto={(a) => !a && setBorrando(null)} titulo="Eliminar conexión" accion="Eliminar" peligro
        descripcion={`Se quitan del .env la API key y la configuración de «${borrando?.nombre}».`}
        onConfirmar={() => { const c = borrando; setBorrando(null); if (c) void eliminar(c); }} />
    </Pagina>
  );
}
