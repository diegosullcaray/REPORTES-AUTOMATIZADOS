import type { Metadata } from "next";
import { LayoutAcceso } from "@/components/layout-acceso";
import { FormularioLogin } from "@/features/auth/formulario-login";

export const metadata: Metadata = { title: "Iniciar sesión · Reportes automatizados" };

export default function PaginaLogin() {
  return (
    <LayoutAcceso>
      <div className="flex flex-col gap-2 text-center">
        <h1 className="text-2xl font-semibold tracking-tight">Iniciar sesión</h1>
        <p className="text-sm text-muted-foreground">Entra con tu usuario y contraseña para gestionar los reportes.</p>
      </div>
      <FormularioLogin />
    </LayoutAcceso>
  );
}
