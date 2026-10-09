// Transporte: única puerta hacia la API de Python (proxy /api en next.config.ts). Sin estado ni presentación.
import type {
  Archivo, ConfiguracionGeneral, Ejecucion, EjecucionDetalle, EstadoEnvio, PedidoEjecucion, Notificaciones, Perfil, PedidoConfiguracion, PedidoCuenta, PedidoNotificaciones, PruebaConexion, PruebaNotificacion, ReporteDetalle, ReporteResumen,
  Servidor, Sesion, Solicitud, Verificacion, VerificacionGrupo, VistaPrevia,
} from "./tipos";

export class ErrorApi extends Error {
  constructor(public estado: number, mensaje: string) {
    super(mensaje);
  }
}

const SIN_API = "No hay conexión con la API de reportes. Arráncala con: python -m uvicorn api.app:app --app-dir src";

function mensajeDe(cuerpo: unknown): string | null {
  const detalle = (cuerpo as { detail?: unknown } | null)?.detail;
  if (typeof detalle === "string") return detalle;
  // 422 de validación de FastAPI: lista de { loc, msg }
  if (Array.isArray(detalle)) return detalle.map((d) => `${(d.loc ?? []).slice(1).join(".")}: ${d.msg}`).join(" · ");
  return null;
}

let yendoALogin = false;

/** Borra la cookie de sesión (es HttpOnly: solo la API puede) y va al login con recarga completa, que descarta caché y estado. Una sola vez aunque fallen varias peticiones. */
export function irALogin() {
  if (yendoALogin) return;
  yendoALogin = true;
  fetch("/api/sesion", { method: "DELETE" })
    .catch(() => undefined)
    .finally(() => {
      // eslint-disable-next-line @next/next/no-location-assign-relative-destination
      window.location.href = "/login";
    });
}

async function pedir<T>(ruta: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`/api${ruta}`, { cache: "no-store", ...init, headers: { "Content-Type": "application/json", ...init?.headers } });
  } catch {
    throw new ErrorApi(0, SIN_API);
  }
  if (!res.ok) {
    // Sesión vencida o inválida: se limpia y se va al login. El intento de login (POST /sesion) maneja su propio 401: «usuario o contraseña incorrectos».
    const esLogin = ruta === "/sesion" && init?.method === "POST";
    if (res.status === 401 && !esLogin && typeof window !== "undefined") irALogin();
    const cuerpo = await res.json().catch(() => null);
    // El proxy devuelve 500 sin JSON cuando la API está apagada.
    throw new ErrorApi(res.status, mensajeDe(cuerpo) ?? (res.status >= 500 ? SIN_API : `Error ${res.status}`));
  }
  return res.json() as Promise<T>;
}

const enviar = (cuerpo: unknown): RequestInit => ({ method: "POST", body: JSON.stringify(cuerpo) });
const r = (nombre: string) => `/reportes/${encodeURIComponent(nombre)}`;
const a = (nombre: string, archivo: string) => `${r(nombre)}/archivos/${encodeURIComponent(archivo)}`;

// El catálogo no cambia mientras la API corre: una sola petición la comparten sidebar y migas.
let catalogo: Promise<ReporteResumen[]> | null = null;

export const api = {
  iniciarSesion: (usuario: string, clave: string) => pedir<Sesion>("/sesion", enviar({ usuario, clave })),
  sesion: () => pedir<Sesion>("/sesion"),
  actualizarCuenta: (cambios: PedidoCuenta) => pedir<Sesion>("/cuenta", { method: "PUT", body: JSON.stringify(cambios) }),
  cerrarSesion: () => fetch("/api/sesion", { method: "DELETE" }),
  reportes: () => (catalogo ??= pedir<ReporteResumen[]>("/reportes").catch((e) => { catalogo = null; throw e; })),
  reporte: (nombre: string) => pedir<ReporteDetalle>(r(nombre)),
  verificar: (nombre: string, fecha_corte: string | null) => pedir<Verificacion>(`${r(nombre)}/verificacion`, enviar({ fecha_corte })),
  verificarGrupo: (grupo: string, fecha_corte: string | null) => pedir<VerificacionGrupo>(`/validacion/${grupo}`, enviar({ fecha_corte })),
  guardarSolicitudGrupo: (grupo: string, fecha_corte: string | null) => pedir<Solicitud>(`/validacion/${grupo}/solicitud`, enviar({ fecha_corte })),
  guardarSolicitud: (nombre: string, fecha_corte: string | null) => pedir<Solicitud>(`${r(nombre)}/solicitud`, enviar({ fecha_corte })),
  archivos: (nombre: string) => pedir<Archivo[]>(`${r(nombre)}/archivos`),
  vistaPrevia: (nombre: string, archivo: string) => pedir<VistaPrevia>(`${a(nombre, archivo)}/vista-previa`),
  estadoEnvio: (nombre: string, fecha_corte: string | null) =>
    pedir<EstadoEnvio>(`${r(nombre)}/envio${fecha_corte ? `?fecha_corte=${fecha_corte}` : ""}`),
  ejecutar: (pedido: PedidoEjecucion) => pedir<Ejecucion>("/ejecuciones", enviar(pedido)),
  ejecuciones: (reporte?: string, limite = 200) =>
    pedir<Ejecucion[]>(`/ejecuciones?limite=${limite}${reporte ? `&reporte=${encodeURIComponent(reporte)}` : ""}`),
  ejecucion: (id: string) => pedir<EjecucionDetalle>(`/ejecuciones/${encodeURIComponent(id)}`),
  perfil: () => pedir<Perfil>("/perfil"),
  configuracion: () => pedir<ConfiguracionGeneral>("/configuracion"),
  guardarConfiguracion: (cambios: PedidoConfiguracion) => pedir<ConfiguracionGeneral>("/configuracion", { method: "PUT", body: JSON.stringify(cambios) }),
  notificaciones: () => pedir<Notificaciones>("/notificaciones"),
  guardarNotificaciones: (cambios: PedidoNotificaciones) => pedir<Notificaciones>("/notificaciones", { method: "PUT", body: JSON.stringify(cambios) }),
  probarNotificacion: (canal: "correo" | "chat") => pedir<PruebaNotificacion>(`/notificaciones/${canal}/prueba`, { method: "POST" }),
  servidores: () => pedir<Servidor[]>("/servidores"),
  probarServidor: (nombre: string) => pedir<PruebaConexion>(`/servidores/${encodeURIComponent(nombre)}/prueba`, { method: "POST" }),
};

/** URL directa de un archivo generado (descarga, o en línea para imágenes). */
export const urlArchivo = (nombre: string, archivo: string, enLinea = false) => `/api${a(nombre, archivo)}${enLinea ? "?en_linea=true" : ""}`;
