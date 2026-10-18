"use client";

import { MoreHorizontal, Trash2 } from "lucide-react";
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { DropdownMenu, DropdownMenuContent, DropdownMenuGroup, DropdownMenuItem, DropdownMenuLabel, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { EliminarReporte } from "../eliminar-reporte";

/** Menú «⋯» de la tarjeta de un reporte (como el del grupo): eliminar pidiendo escribir el nombre. El backend solo borra los creados desde la web. */
export function MenuReporte({ nombre }: { nombre: string }) {
  const [confirmar, setConfirmar] = useState(false);
  return (
    <>
      <DropdownMenu>
        <DropdownMenuTrigger render={<Button variant="ghost" size="icon" className="px-2" aria-label={`Acciones de ${nombre}`} />}>
          <MoreHorizontal className="size-5" />
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end" className="w-[200px]">
          <DropdownMenuGroup>
            <DropdownMenuLabel className="font-normal">Acciones</DropdownMenuLabel>
          </DropdownMenuGroup>
          <DropdownMenuItem className="cursor-pointer gap-3" onClick={() => setConfirmar(true)}><Trash2 className="size-4" /> Eliminar</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
      <EliminarReporte nombre={nombre} abierto={confirmar} onAbierto={setConfirmar} />
    </>
  );
}
