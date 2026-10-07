import { Suspense } from "react";
import { PanelPerfil } from "@/features/perfil/panel-perfil";

export default function PaginaPerfil() {
  return (
    <Suspense>
      <PanelPerfil />
    </Suspense>
  );
}
