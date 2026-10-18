"use client";

import { Eye, EyeOff, LogOut, Save, UserRound } from "lucide-react";
import { useState, type FormEvent, type ReactNode } from "react";
import { toast } from "sonner";
import { ErrorEnLinea } from "@/components/estados";
import { Marco } from "@/components/marco";
import { Pagina } from "@/components/pagina";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useConsulta } from "@/hooks/use-consulta";
import { api, irALogin } from "@/lib/api";
import { iniciales } from "@/lib/formato";
import { COLORES_AVATAR, guardarAvatar, useAvatar } from "@/hooks/use-avatar";

function Campo({ id, etiqueta, ayuda, children }: { id: string; etiqueta: string; ayuda?: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-1.5">
      <Label htmlFor={id}>{etiqueta}</Label>
      {children}
      {ayuda && <span className="text-xs text-muted-foreground">{ayuda}</span>}
    </div>
  );
}

/** Contraseña con botón para verla (como en el login). */
function Clave({ id, valor, onCambio, autoComplete }: { id: string; valor: string; onCambio: (v: string) => void; autoComplete: string }) {
  const [visible, setVisible] = useState(false);
  return (
    <div className="relative">
      <Input id={id} type={visible ? "text" : "password"} value={valor} onChange={(ev) => onCambio(ev.target.value)} autoComplete={autoComplete} className="pr-10" />
      <Button type="button" variant="ghost" size="icon-sm" className="absolute top-1/2 right-1 -translate-y-1/2" aria-pressed={visible}
        aria-label={visible ? "Ocultar contraseña" : "Mostrar contraseña"} onClick={() => setVisible((v) => !v)}>{visible ? <EyeOff /> : <Eye />}</Button>
    </div>
  );
}

/** Formulario de la cuenta (como «Profile» de Dokploy): cambiar usuario y contraseña, siempre con la contraseña actual. */
function FormularioCuenta({ usuario }: { usuario: string }) {
  const [nuevoUsuario, setNuevoUsuario] = useState(usuario);
  const [actual, setActual] = useState("");
  const [nueva, setNueva] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const cambiaUsuario = nuevoUsuario.trim() !== usuario;
  const hayCambios = cambiaUsuario || nueva !== "";
  const noCoincide = nueva !== "" && nueva !== confirmar;

  async function guardar(ev: FormEvent) {
    ev.preventDefault();
    if (!hayCambios || noCoincide) return;
    setGuardando(true);
    setError(null);
    try {
      await api.actualizarCuenta({ clave_actual: actual, ...(cambiaUsuario && { usuario: nuevoUsuario.trim() }), ...(nueva && { clave_nueva: nueva }) });
      toast.success("Cuenta actualizada", { description: "Se guardó en el .env y rige desde ahora." });
      if (cambiaUsuario) window.location.reload(); // el sidebar muestra el usuario de la sesión anterior hasta recargar
      setActual("");
      setNueva("");
      setConfirmar("");
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setGuardando(false);
    }
  }

  return (
    <form onSubmit={guardar} className="flex max-w-xl flex-col gap-4">
      <Campo id="usuario" etiqueta="Usuario"><Input id="usuario" value={nuevoUsuario} onChange={(ev) => setNuevoUsuario(ev.target.value)} autoComplete="username" /></Campo>
      <Campo id="clave-actual" etiqueta="Contraseña actual" ayuda="Obligatoria para guardar cualquier cambio."><Clave id="clave-actual" valor={actual} onCambio={setActual} autoComplete="current-password" /></Campo>
      <Campo id="clave-nueva" etiqueta="Contraseña nueva" ayuda="Opcional. Mínimo 8 caracteres; sin #, comillas ni saltos de línea."><Clave id="clave-nueva" valor={nueva} onCambio={setNueva} autoComplete="new-password" /></Campo>
      {nueva !== "" && <Campo id="clave-confirmar" etiqueta="Repite la contraseña nueva"><Clave id="clave-confirmar" valor={confirmar} onCambio={setConfirmar} autoComplete="new-password" /></Campo>}
      {noCoincide && <p className="text-sm text-[var(--mis-danger)]">Las contraseñas no coinciden.</p>}
      {error && <ErrorEnLinea titulo="No se guardó" detalle={error} />}
      <div><Button type="submit" disabled={!hayCambios || !actual || noCoincide || guardando}><Save /> {guardando ? "Guardando…" : "Guardar cambios"}</Button></div>
    </form>
  );
}

/** Selector de avatar (como el de «Account» en Dokploy): iniciales sobre el color elegido. */
function SelectorAvatar({ usuario }: { usuario: string }) {
  const color = useAvatar();
  return (
    <div className="flex flex-col gap-1.5">
      <Label>Avatar</Label>
      <div className="flex flex-wrap gap-2" role="radiogroup" aria-label="Color del avatar">
        {COLORES_AVATAR.map((c) => (
          <button key={c || "marca"} type="button" role="radio" aria-checked={color === c} aria-label={c ? `Color ${c}` : "Color de marca"} onClick={() => guardarAvatar(c)}
            style={{ background: c || "var(--mis-primary)" }}
            className={`flex size-12 items-center justify-center rounded-full text-sm font-semibold text-primary-foreground ${color === c ? "ring-2 ring-offset-2 ring-offset-background ring-[var(--mis-primary-text)]" : "hover:ring-2 hover:ring-border"}`}>
            {iniciales(usuario)}
          </button>
        ))}
      </div>
    </div>
  );
}

/** Perfil (como «Account» de Dokploy): un solo marco con la cuenta (avatar, usuario, contraseña) y, en el encabezado, cerrar sesión. */
export function PanelCuenta() {
  const sesion = useConsulta("sesion", api.sesion);
  const perfil = useConsulta("perfil", api.perfil);
  const usuario = sesion.datos?.usuario;
  const p = perfil.datos;

  return (
    <Pagina>
      <Marco icono={<UserRound />} titulo="Cuenta"
        descripcion={`Cambia los datos con que entras a la web; se guardan en el .env de la API.${p ? ` La API corre en ${p.equipo} como ${p.usuario}; la sesión dura 8 horas.` : ""}`}
        acciones={<Button variant="outline" size="sm" onClick={() => api.cerrarSesion().finally(irALogin)}><LogOut /> Cerrar sesión</Button>}>
        {usuario && <SelectorAvatar usuario={usuario} />}
        {usuario && <FormularioCuenta key={usuario} usuario={usuario} />}
      </Marco>
    </Pagina>
  );
}
