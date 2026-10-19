// Transporte: única puerta hacia la API de Python (proxy /api en next.config.ts). Sin estado ni presentación.
import type {
  Archivo, ConfigIA, Etiqueta, GrupoReportes, ConfiguracionGeneral, ModelosIA, PedidoIA, DestinosChat, EntradaValidacion, FirmaGmail, PedidoEnvioArchivos, Ejecucion, EjecucionDetalle, EstadoEnvio, PedidoEjecucion, Notificaciones, Perfil, PedidoConfiguracion, PedidoCuenta, PedidoNotificaciones, PruebaNotificacion, ReporteDetalle, PedidoReporteNuevo, ReporteCreado, ReporteResumen, Script,
  DicBaseDetalle, DicBaseFila, DicEjecucion, DicEjecucionDetalle, DicHallazgo, DicPotencial, DicProceso, DicProcesoDetalle, DicReporteDetalle, DicResumen, DicTablaDetalle,
  GoogleMcp, PedidoGoogleMcp, PruebaMcp, Sesion, Solicitud, Verificacion, VerificacionGrupo, VistaPrevia,
} from "./tipos";

export class ErrorApi extends Error {
  constructor(public estado: number, mensaje: string) {
    super(mensaje);
  }
}

const SIN_API = "No hay conexión con la API de reportes. Arráncala con: python manage.py runserver 127.0.0.1:8000 --noreload";

function mensajeDe(cuerpo: unknown): string | null {
  const detalle = (cuerpo as { detail?: unknown } | null)?.detail;
  if (typeof detalle === "string") return detalle;
  // 422 de validación: lista de { loc, msg, type } (la devuelve core/http.py)
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
  grupos: () => pedir<GrupoReportes[]>("/grupos"),
  crearGrupo: (p: { nombre: string; etiquetas: string[] }) => pedir<GrupoReportes>("/grupos", enviar(p)),
  etiquetasDeGrupo: (id: string, etiquetas: string[]) => pedir<GrupoReportes>(`/grupos/${encodeURIComponent(id)}/etiquetas`, { method: "PUT", body: JSON.stringify({ etiquetas }) }),
  etiquetas: () => pedir<Etiqueta[]>("/etiquetas"),
  crearEtiqueta: (p: { nombre: string; color: string }) => pedir<Etiqueta>("/etiquetas", enviar(p)),
  actualizarEtiqueta: (id: string, p: { nombre: string; color: string }) => pedir<Etiqueta>(`/etiquetas/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify(p) }),
  eliminarEtiqueta: (id: string) => pedir<{ ok: boolean }>(`/etiquetas/${encodeURIComponent(id)}`, { method: "DELETE" }),
  eliminarGrupo: (id: string) => pedir<{ ok: boolean }>(`/grupos/${encodeURIComponent(id)}`, { method: "DELETE" }),
  crearReporte: (p: PedidoReporteNuevo) => {
    catalogo = null; // el catálogo cambia: la próxima lectura lo pide de nuevo
    return pedir<ReporteCreado>("/reportes", enviar(p));
  },
  reporte: (nombre: string) => pedir<ReporteDetalle>(r(nombre)),
  eliminarReporte: (nombre: string) => {
    catalogo = null;
    return pedir<{ ok: boolean }>(r(nombre), { method: "DELETE" });
  },
  guardarChatReporte: (nombre: string, destinatarios: string) => pedir<ReporteDetalle>(`${r(nombre)}/chat`, { method: "PUT", body: JSON.stringify({ destinatarios }) }),
  guardarDestinosCorreo: (nombre: string, para: string, cc: string) => pedir<ReporteDetalle>(`${r(nombre)}/correo-destinos`, { method: "PUT", body: JSON.stringify({ para, cc }) }),
  enviarArchivosCorreo: (nombre: string, pedido: PedidoEnvioArchivos) => pedir<PruebaNotificacion>(`${r(nombre)}/correo/enviar`, enviar(pedido)),
  firmaGmail: () => pedir<FirmaGmail>("/google/firma"),
  verificar: (nombre: string, fecha_corte: string | null) => pedir<Verificacion>(`${r(nombre)}/verificacion`, enviar({ fecha_corte })),
  verificarGrupo: (grupo: string, fecha_corte: string | null) => pedir<VerificacionGrupo>(`/validacion/${grupo}`, enviar({ fecha_corte })),
  historialValidacion: (grupo: string, limite = 50) => pedir<EntradaValidacion[]>(`/validacion/${grupo}/historial?limite=${limite}`),
  destinosChatValidacion: (grupo: string) => pedir<DestinosChat>(`/validacion/${grupo}/chat`),
  guardarDestinosChatValidacion: (grupo: string, destinatarios: string) => pedir<DestinosChat>(`/validacion/${grupo}/chat`, { method: "PUT", body: JSON.stringify({ destinatarios }) }),
  enviarChatValidacion: (grupo: string) => pedir<PruebaNotificacion>(`/validacion/${grupo}/chat/enviar`, { method: "POST" }),
  guardarSolicitudGrupo: (grupo: string, fecha_corte: string | null) => pedir<Solicitud>(`/validacion/${grupo}/solicitud`, enviar({ fecha_corte })),
  guardarSolicitud: (nombre: string, fecha_corte: string | null) => pedir<Solicitud>(`${r(nombre)}/solicitud`, enviar({ fecha_corte })),
  archivos: (nombre: string) => pedir<Archivo[]>(`${r(nombre)}/archivos`),
  script: (nombre: string) => pedir<Script>(`${r(nombre)}/script`),
  guardarScript: (nombre: string, codigo: string) => pedir<Script>(`${r(nombre)}/script`, { method: "PUT", body: JSON.stringify({ codigo }) }),
  vistaPrevia: (nombre: string, archivo: string) => pedir<VistaPrevia>(`${a(nombre, archivo)}/vista-previa`),
  estadoEnvio: (nombre: string, fecha_corte: string | null) =>
    pedir<EstadoEnvio>(`${r(nombre)}/envio${fecha_corte ? `?fecha_corte=${fecha_corte}` : ""}`),
  ejecutar: (pedido: PedidoEjecucion) => pedir<Ejecucion>("/ejecuciones", enviar(pedido)),
  ejecuciones: (reporte?: string, limite = 200) =>
    pedir<Ejecucion[]>(`/ejecuciones?limite=${limite}${reporte ? `&reporte=${encodeURIComponent(reporte)}` : ""}`),
  eliminarEjecuciones: (ids: string[]) => pedir<{ eliminadas: number }>("/ejecuciones/eliminar", enviar({ ids })),
  ejecucion: (id: string) => pedir<EjecucionDetalle>(`/ejecuciones/${encodeURIComponent(id)}`),
  perfil: () => pedir<Perfil>("/perfil"),
  dic: {
    resumen: () => pedir<DicResumen>("/diccionario/resumen"),
    potencial: () => pedir<DicPotencial>("/diccionario/potencial"),
    hallazgos: () => pedir<DicHallazgo[]>("/diccionario/hallazgos"),
    bases: () => pedir<DicBaseFila[]>("/diccionario/bases"),
    base: (nombre: string) => pedir<DicBaseDetalle>(`/diccionario/bases/${encodeURIComponent(nombre)}`),
    reporte: (codigo: string) => pedir<DicReporteDetalle>(`/diccionario/reportes/${encodeURIComponent(codigo)}`),
    tabla: (nombre: string) => pedir<DicTablaDetalle>(`/diccionario/tablas/${encodeURIComponent(nombre)}`),
    procesos: () => pedir<DicProceso[]>("/diccionario/procesos"),
    proceso: (id: string) => pedir<DicProcesoDetalle>(`/diccionario/procesos/${encodeURIComponent(id)}`),
    ejecutar: (id: string) => pedir<DicEjecucion>(`/diccionario/procesos/${encodeURIComponent(id)}/ejecutar`, { method: "POST" }),
    ejecuciones: (proceso?: string) => pedir<DicEjecucion[]>(`/diccionario/ejecuciones${proceso ? `?proceso=${encodeURIComponent(proceso)}` : ""}`),
    ejecucion: (id: string) => pedir<DicEjecucionDetalle>(`/diccionario/ejecuciones/${encodeURIComponent(id)}`),
  },
  configuracion: () => pedir<ConfiguracionGeneral>("/configuracion"),
  guardarConfiguracion: (cambios: PedidoConfiguracion) => pedir<ConfiguracionGeneral>("/configuracion", { method: "PUT", body: JSON.stringify(cambios) }),
  ia: () => pedir<ConfigIA[]>("/ia"),
  crearIA: (p: PedidoIA) => pedir<ConfigIA>("/ia", enviar(p)),
  actualizarIA: (id: string, p: Partial<PedidoIA>) => pedir<ConfigIA>(`/ia/${encodeURIComponent(id)}`, { method: "PUT", body: JSON.stringify(p) }),
  eliminarIA: (id: string) => pedir<{ ok: boolean }>(`/ia/${encodeURIComponent(id)}`, { method: "DELETE" }),
  modelosIA: (p: { api_url: string; api_key: string; id?: string }) => pedir<ModelosIA>("/ia/modelos", enviar(p)),
  probarIA: (id: string) => pedir<ModelosIA>(`/ia/${encodeURIComponent(id)}/probar`, enviar({})),
  notificaciones: () => pedir<Notificaciones>("/notificaciones"),
  guardarNotificaciones: (cambios: PedidoNotificaciones) => pedir<Notificaciones>("/notificaciones", { method: "PUT", body: JSON.stringify(cambios) }),
  googleMcp: () => pedir<GoogleMcp>("/mcp/google"),
  guardarGoogleMcp: (cambios: PedidoGoogleMcp) => pedir<GoogleMcp>("/mcp/google", { method: "PUT", body: JSON.stringify(cambios) }),
  autorizarGoogle: (redirect_uri: string) => pedir<{ url: string; redirect_uri: string }>("/mcp/google/autorizar", enviar({ redirect_uri })),
  codigoGoogle: (codigo: string, state?: string) => pedir<GoogleMcp>("/mcp/google/codigo", enviar({ codigo, state })),
  desconectarGoogle: () => pedir<GoogleMcp>("/mcp/google/autorizacion", { method: "DELETE" }),
  herramientasGoogle: (servicio: string) => pedir<PruebaMcp>(`/mcp/google/${encodeURIComponent(servicio)}/herramientas`, { method: "POST" }),
  ejecutarGoogle: (servicio: string, herramienta: string, argumentos: Record<string, unknown>) =>
    pedir<PruebaNotificacion>(`/mcp/google/${encodeURIComponent(servicio)}/ejecutar`, enviar({ herramienta, argumentos })),
  enviarGoogle: (servicio: string, destinatario: string, texto: string) => pedir<PruebaNotificacion>(`/mcp/google/${encodeURIComponent(servicio)}/enviar`, enviar({ destinatario, texto })),
  probarNotificacion: (canal: "correo" | "chat") => pedir<PruebaNotificacion>(`/notificaciones/${canal}/prueba`, { method: "POST" }),
};

/** URL directa de un archivo generado (descarga, o en línea para imágenes). */
export const urlArchivo = (nombre: string, archivo: string, enLinea = false) => `/api${a(nombre, archivo)}${enLinea ? "?en_linea=true" : ""}`;
