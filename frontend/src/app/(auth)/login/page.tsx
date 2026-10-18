import type { Metadata } from "next";
import { LayoutAcceso } from "@/components/layout-acceso";
import { FormularioLogin } from "@/features/auth/formulario-login";

export const metadata: Metadata = { title: "Iniciar sesión · Reportes automatizados" };

export default function PaginaLogin() {
  return (
    <LayoutAcceso>
      <FormularioLogin />
    </LayoutAcceso>
  );
}
