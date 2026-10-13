// Agrupa las ejecuciones por reporte y fecha de corte y arma su proceso paso a paso. Funciones puras (sin React).
import type { Ejecucion } from "../../lib/tipos";

export type EstadoPaso = "hecho" | "fallo" | "falta" | "en_curso";
export type EstadoProceso = "completo" | "incompleto" | "fallo" | "en_curso";

export interface Paso {
  id: string;
  nombre: string;
  estado: EstadoPaso;
  /** Último intento que tocó este paso (null si falta). */
  ejecucion: Ejecucion | null;
  intentos: number;
}

export interface Proceso {
  clave: string;
  reporte: string;
  corte: string | null;
  ejecuciones: Ejecucion[];
  pasos: Paso[];
  estado: EstadoProceso;
  ultima: string;
}

const EN_CURSO = new Set<Ejecucion["estado"]>(["en_cola", "ejecutando"]);

const corteDe = (args: string[]) => {
  const i = args.findIndex((a) => a === "--fecha-corte" || a === "--mes");
  return i >= 0 ? args[i + 1] ?? null : null;
};
const correoDe = (args: string[]) => {
  const i = args.indexOf("--correo");
  return i >= 0 ? args[i + 1] ?? "prueba" : null;
};
const hizoExcel = (x: Ejecucion) => x.archivos.some((a) => /\.xls[xm]$/i.test(a));

/** Resultado de una ejecución sobre un paso, o null si no lo toca. */
type Efecto = (x: Ejecucion) => EstadoPaso | null;
const resultado = (x: Ejecucion): EstadoPaso => (EN_CURSO.has(x.estado) ? "en_curso" : x.estado === "ok" ? "hecho" : "fallo");

/** Reportes con correo (Cartera sin asignar): Excel → prueba → envío a la lista. */
const PASOS_CORREO: { id: string; nombre: string; efecto: Efecto }[] = [
  {
    id: "excel", nombre: "Excel generado",
    efecto: (x) => (correoDe(x.argumentos) === "todos" ? null : resultado(x) === "fallo" && hizoExcel(x) ? "hecho" : resultado(x)),
  },
  { id: "prueba", nombre: "Correo de prueba", efecto: (x) => (correoDe(x.argumentos) === "prueba" ? (resultado(x) === "fallo" && !hizoExcel(x) ? null : resultado(x)) : null) },
  { id: "envio", nombre: "Envío a la lista", efecto: (x) => (correoDe(x.argumentos) === "todos" ? resultado(x) : null) },
];
const PASOS_SIMPLES: { id: string; nombre: string; efecto: Efecto }[] = [{ id: "generacion", nombre: "Generación", efecto: resultado }];

function armar(reporte: string, corte: string | null, ejecuciones: Ejecucion[]): Proceso {
  const recientes = [...ejecuciones].sort((a, b) => b.inicio.localeCompare(a.inicio));
  const definicion = recientes.some((x) => correoDe(x.argumentos) !== null) ? PASOS_CORREO : PASOS_SIMPLES;
  const pasos = definicion.map(({ id, nombre, efecto }): Paso => {
    const tocan = recientes.filter((x) => efecto(x) !== null);
    const ultima = tocan[0] ?? null;
    return { id, nombre, estado: ultima ? efecto(ultima)! : "falta", ejecucion: ultima, intentos: tocan.length };
  });
  const estado: EstadoProceso = pasos.some((p) => p.estado === "en_curso") ? "en_curso"
    : pasos.some((p) => p.estado === "fallo") ? "fallo"
    : pasos.every((p) => p.estado === "hecho") ? "completo" : "incompleto";
  return { clave: `${reporte}|${corte ?? ""}`, reporte, corte, ejecuciones: recientes, pasos, estado, ultima: recientes[0]?.inicio ?? "" };
}

/** Un proceso por reporte y fecha de corte, del más reciente al más antiguo. */
export function agruparProcesos(ejecuciones: Ejecucion[]): Proceso[] {
  const grupos = new Map<string, { reporte: string; corte: string | null; ejecuciones: Ejecucion[] }>();
  for (const x of ejecuciones) {
    const corte = corteDe(x.argumentos);
    const clave = `${x.reporte}|${corte ?? ""}`;
    const g = grupos.get(clave) ?? { reporte: x.reporte, corte, ejecuciones: [] };
    g.ejecuciones.push(x);
    grupos.set(clave, g);
  }
  return [...grupos.values()].map((g) => armar(g.reporte, g.corte, g.ejecuciones)).sort((a, b) => b.ultima.localeCompare(a.ultima));
}
