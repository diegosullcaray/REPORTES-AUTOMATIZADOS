"use client";

import type { ReactNode } from "react";
import {
  AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter,
  AlertDialogHeader, AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface Props {
  abierto: boolean;
  onAbierto: (v: boolean) => void;
  titulo: string;
  descripcion: ReactNode;
  children?: ReactNode;
  accion: string;
  peligro?: boolean;
  deshabilitado?: boolean;
  onConfirmar: () => void;
}

/** Confirmación explícita antes de una acción con efectos (ejecutar, escribir en BD, enviar correo). */
export function Confirmar({ abierto, onAbierto, titulo, descripcion, children, accion, peligro, deshabilitado, onConfirmar }: Props) {
  return (
    <AlertDialog open={abierto} onOpenChange={onAbierto}>
      <AlertDialogContent className="sm:max-w-md" style={{ border: "1px solid var(--mis-dialog-border)", boxShadow: "var(--mis-shadow-lg)" }}>
        <AlertDialogHeader>
          <AlertDialogTitle>{titulo}</AlertDialogTitle>
          <AlertDialogDescription render={<div />}>{descripcion}</AlertDialogDescription>
        </AlertDialogHeader>
        {children}
        <AlertDialogFooter>
          <AlertDialogCancel>Cancelar</AlertDialogCancel>
          <AlertDialogAction variant={peligro ? "destructive" : "default"} disabled={deshabilitado} onClick={onConfirmar}>{accion}</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
