import { useSyncExternalStore } from "react";

const CLAVE = "mis-avatar";

/** Colores del avatar (solo tokens `--mis-*`); "" = el color de marca por defecto. */
export const COLORES_AVATAR = ["", "var(--mis-success)", "var(--mis-warning)", "var(--mis-danger)"] as const;

const oyentes = new Set<() => void>();

function leer(): string {
  try {
    return localStorage.getItem(CLAVE) ?? "";
  } catch {
    return ""; // sin almacenamiento (ventana privada): se usa el color por defecto
  }
}

/** Color elegido para el avatar. Vive en el navegador (la cuenta es un usuario del .env, sin perfil en la API). */
export function guardarAvatar(color: string) {
  try {
    localStorage.setItem(CLAVE, color);
  } catch { /* sin almacenamiento: el cambio rige solo hasta recargar */ }
  oyentes.forEach((o) => o());
}

export function useAvatar(): string {
  return useSyncExternalStore((cb) => { oyentes.add(cb); return () => void oyentes.delete(cb); }, leer, () => "");
}
