"use client";

import { Eye, EyeOff, LogIn } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { toast } from "sonner";
import { Aviso } from "@/components/estados";
import { Button } from "@/components/ui/button";
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { api } from "@/lib/api";

/** Usuario y contraseña definidos en el .env de la API; ella los valida y deja la cookie de sesión. */
export function FormularioLogin() {
  const router = useRouter();
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [visible, setVisible] = useState(false);

  const entrar = async (ev: FormEvent<HTMLFormElement>) => {
    ev.preventDefault();
    const datos = new FormData(ev.currentTarget);
    setEnviando(true);
    setError(null);
    try {
      await api.iniciarSesion(String(datos.get("usuario")).trim(), String(datos.get("clave")));
      toast.success("Sesión iniciada");
      router.replace("/");
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo iniciar sesión");
      setEnviando(false);
    }
  };

  return (
    <form onSubmit={entrar}>
      <FieldGroup>
        <div className="flex flex-col items-center gap-2 text-center">
          <h1 className="text-2xl font-bold">Iniciar sesión</h1>
          <p className="text-balance text-muted-foreground">Entra con tu usuario y contraseña para gestionar los reportes.</p>
        </div>
        {error && <Aviso tono="peligro">{error}</Aviso>}
        <Field>
          <FieldLabel htmlFor="usuario">Usuario</FieldLabel>
          <Input id="usuario" name="usuario" autoComplete="username" required autoFocus />
        </Field>
        <Field>
          <FieldLabel htmlFor="clave">Contraseña</FieldLabel>
          <div className="relative">
            <Input id="clave" name="clave" type={visible ? "text" : "password"} autoComplete="current-password" className="pr-10" required />
            <Button type="button" variant="ghost" size="icon-sm" className="absolute top-1/2 right-1 -translate-y-1/2"
              aria-label={visible ? "Ocultar contraseña" : "Mostrar contraseña"} aria-pressed={visible} onClick={() => setVisible((v) => !v)}>
              {visible ? <EyeOff /> : <Eye />}
            </Button>
          </div>
        </Field>
        <Field>
          <Button type="submit" disabled={enviando}><LogIn /> {enviando ? "Verificando…" : "Iniciar sesión"}</Button>
        </Field>
      </FieldGroup>
    </form>
  );
}
