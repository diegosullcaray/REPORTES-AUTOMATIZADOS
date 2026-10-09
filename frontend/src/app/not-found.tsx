import { PaginaError } from "@/components/pagina-error";

/** 404 de cualquier ruta que no exista (y de `notFound()`), dentro del layout raíz para conservar el tema. */
export default function NoEncontrada() {
  return <PaginaError codigo={404} mensaje="Lo sentimos, no encontramos esa página." />;
}
