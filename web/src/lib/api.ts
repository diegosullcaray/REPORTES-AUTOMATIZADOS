// Transporte: única puerta hacia la API de Python (proxy /api en next.config.ts). Sin estado ni presentación.
import type {
  Archivo, Ejecucion, EjecucionDetalle, EstadoEnvio, PedidoEjecucion, ReporteDetalle, ReporteResumen, Solicitud,
  Verificacion, VistaPrevia,
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

async function pedir<T>(ruta: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`/api${ruta}`, { cache: "no-store", ...init, headers: { "Content-Type": "application/json", ...init?.headers } });
  } catch {
    throw new ErrorApi(0, SIN_API);
  }
  if (!res.ok) {
    const cuerpo = await res.json().catch(() => null);
    // El proxy devuelve 500 sin JSON cuando la API está apagada.
    throw new ErrorApi(res.status, mensajeDe(cuerpo) ?? (res.status >= 500 ? SIN_API : `Error ${res.status}`));
  }
  return res.json() as Promise<T>;
}

const enviar = (cuerpo: unknown): RequestInit => ({ method: "POST", body: JSON.stringify(cuerpo) });
const r = (nombre: string) => `/reportes/${encodeURIComponent(nombre)}`;
const a = (nombre: string, archivo: string) => `${r(nombre)}/archivos/${encodeURIComponent(archivo)}`;

export const api = {
  reportes: () => pedir<ReporteResumen[]>("/reportes"),
  reporte: (nombre: string) => pedir<ReporteDetalle>(r(nombre)),
  verificar: (nombre: string, fecha_corte: string | null) => pedir<Verificacion>(`${r(nombre)}/verificacion`, enviar({ fecha_corte })),
  guardarSolicitud: (nombre: string, fecha_corte: string | null) => pedir<Solicitud>(`${r(nombre)}/solicitud`, enviar({ fecha_corte })),
  archivos: (nombre: string) => pedir<Archivo[]>(`${r(nombre)}/archivos`),
  vistaPrevia: (nombre: string, archivo: string) => pedir<VistaPrevia>(`${a(nombre, archivo)}/vista-previa`),
  estadoEnvio: (nombre: string, fecha_corte: string | null) =>
    pedir<EstadoEnvio>(`${r(nombre)}/envio${fecha_corte ? `?fecha_corte=${fecha_corte}` : ""}`),
  ejecutar: (pedido: PedidoEjecucion) => pedir<Ejecucion>("/ejecuciones", enviar(pedido)),
  ejecuciones: (reporte?: string) => pedir<Ejecucion[]>(`/ejecuciones${reporte ? `?reporte=${encodeURIComponent(reporte)}` : ""}`),
  ejecucion: (id: string) => pedir<EjecucionDetalle>(`/ejecuciones/${encodeURIComponent(id)}`),
  conexiones: () => pedir<Record<string, string>>("/conexiones"),
};

/** URL directa de un archivo generado (descarga, o en línea para imágenes). */
export const urlArchivo = (nombre: string, archivo: string, enLinea = false) => `/api${a(nombre, archivo)}${enLinea ? "?en_linea=true" : ""}`;
