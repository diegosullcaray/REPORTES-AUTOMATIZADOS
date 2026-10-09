"use client";

import { Moon, Sun } from "lucide-react";
import { useTheme } from "next-themes";
import { Button } from "@/components/ui/button";

/** Botón claro/oscuro (como el ModeToggle de Dokploy). Los íconos cambian por CSS (`dark:`), así no hay desajuste de hidratación. */
export function ModoTema({ className }: { className?: string }) {
  const { resolvedTheme, setTheme } = useTheme();
  return (
    <Button variant="outline" size="icon" className={className} onClick={() => setTheme(resolvedTheme === "dark" ? "light" : "dark")}>
      <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
      <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
      <span className="sr-only">Cambiar tema</span>
    </Button>
  );
}
