// Espejo de src/api/esquemas.py. Si cambia un contrato allá, se cambia aquí.

export type Grupo = "diarias" | "piero" | "erick";
export type Frecuencia = "diaria" | "mensual";

export interface ReporteResumen {
  nombre: string;
  grupo: Grupo;
  orden: string;
  frecuencia: Frecuencia;
  servidores: string[];
  descripcion: string;
  carpeta: string;
  es_lote: boolean;
  escribe_en_bd: boolean;
  vacio_valido: boolean;
  envia_correo: boolean;
  avisos: string[];
}

export interface Corte {
  fecha: string | null;
  origen: string;
}

export interface TablaReporte {
  nombre: string;
  servidor: string;
  tipo: string;
  columna_fecha: string | null;
  confianza: string;
  verificable: boolean;
  condicion: string | null;
}

export interface ReporteDetalle extends ReporteResumen {
  corte: Corte;
  tablas: TablaReporte[];
}

export type EstadoTabla = "OK" | "DESACTUALIZADA" | "NO EXISTE" | "ERROR" | "SIN CONTROL";

export interface ResultadoTabla {
  nombre: string;
  servidor: string;
  estado: EstadoTabla;
  ultima_fecha: string | null;
  detalle: string;
}

export interface Verificacion {
  corte: string;
  listo: boolean;
  resultados: ResultadoTabla[];
  solicitud: string | null;
}

export interface Solicitud {
  archivo: string;
  texto: string;
}

export type Correo = "no" | "prueba" | "todos";

export interface PedidoEjecucion {
  reporte: string;
  fecha_corte: string | null;
  forzar?: boolean;
  confirmar_escritura?: boolean;
  correo?: Correo;
  conforme?: boolean;
}

export type EstadoEjecucion = "en_cola" | "ejecutando" | "ok" | "error" | "configuracion" | "tablas_desactualizadas";

export interface Ejecucion {
  id: string;
  reporte: string;
  argumentos: string[];
  estado: EstadoEjecucion;
  codigo: number | null;
  inicio: string;
  fin: string | null;
  archivos: string[];
}

export interface EjecucionDetalle extends Ejecucion {
  log: string;
}

export type TipoArchivo = "excel" | "imagen" | "texto" | "otro";

export interface Archivo {
  nombre: string;
  tipo: TipoArchivo;
  tamano: number;
  modificado: string;
}

export type Celda = string | number | null;

export interface HojaPrevia {
  nombre: string;
  columnas: string[];
  filas: Celda[][];
  total_filas: number;
}

export interface VistaPrevia {
  archivo: string;
  tipo: "excel" | "texto";
  hojas: HojaPrevia[];
  texto: string | null;
}

export interface EstadoEnvio {
  corte: string;
  prueba: string | null;
  todos: string | null;
  excel: string | null;
}
