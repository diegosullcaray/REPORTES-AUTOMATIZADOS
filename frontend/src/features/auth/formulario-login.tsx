"use client";

import { LogIn } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";
import { toast } from "sonner";
import { Aviso } from "@/components/estados";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { api } from "@/lib/api";

/** Usuario y contraseña definidos en el .env de la API; ella los valida y deja la cookie de sesión. */
export function FormularioLogin() {
  const router = useRouter();
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);

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
    <form onSubmit={entrar} className="flex flex-col gap-4">
      {error && <Aviso tono="peligro">{error}</Aviso>}
      <div className="flex flex-col gap-2">
        <Label htmlFor="usuario">Usuario</Label>
        <Input id="usuario" name="usuario" autoComplete="username" required autoFocus />
      </div>
      <div className="flex flex-col gap-2">
        <Label htmlFor="clave">Contraseña</Label>
        <Input id="clave" name="clave" type="password" autoComplete="current-password" required />
      </div>
      <Button type="submit" className="w-full" disabled={enviando}><LogIn /> {enviando ? "Verificando…" : "Iniciar sesión"}</Button>
    </form>
  );
}
