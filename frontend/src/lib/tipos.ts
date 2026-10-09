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

export interface TablaValidada extends ResultadoTabla {
  reportes: string[];
}

export interface ResumenValidacion {
  nombre: string;
  orden: string;
  tablas: number;
  pendientes: number;
  dudosas: number;
  listo: boolean;
}

/** Causa de error compartida por varias tablas (conexión, credenciales, driver), con su solución. */
export interface ProblemaValidacion {
  causa: string;
  tablas: number;
  solucion: string;
}

/** Validación masiva: todas las tablas de los reportes mensuales de un responsable, cada una verificada una vez. */
export interface VerificacionGrupo {
  grupo: string;
  titulo: string;
  corte: string;
  listo: boolean;
  reportes: ResumenValidacion[];
  tablas: TablaValidada[];
  problemas?: ProblemaValidacion[]; // una API anterior no lo envía
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

export interface Servidor {
  nombre: string;
  servidor: string;
  autenticacion: "Windows" | "SQL";
  credenciales_en_env: boolean;
  descripcion: string;
  bases: string[];
}

export interface PruebaConexion {
  nombre: string;
  ok: boolean;
  detalle: string;
  milisegundos: number;
}

export interface Perfil {
  usuario: string;
  equipo: string;
  correo_prueba: string;
  cuenta_envio: string | null;
  clave_envio_configurada: boolean;
  webhook_configurado: boolean;
  destinatarios: number | null;
}

export interface ConfiguracionGeneral {
  corte_mensual: Corte;
  corte_diario: Corte;
  dir_inputs: string;
  dir_outputs: string;
  driver_odbc: string;
  pendientes_reinicio: string[];
}

/** Correo y Google Chat. La clave y el webhook nunca llegan al navegador: solo si están configurados. */
export interface Notificaciones {
  smtp_host: string;
  smtp_port: number;
  smtp_user: string;
  remitente_nombre: string;
  correo_prueba: string;
  clave_configurada: boolean;
  webhook_configurado: boolean;
  destinatarios: number | null;
}

/** Solo se envían los campos cambiados; texto vacío = quitar la variable del .env. */
export interface PedidoNotificaciones {
  smtp_host?: string;
  smtp_port?: string;
  smtp_user?: string;
  smtp_clave?: string;
  remitente_nombre?: string;
  correo_prueba?: string;
  webhook?: string;
}

export interface PruebaNotificacion {
  ok: boolean;
  detalle: string;
}

/** Solo se envían los campos cambiados; texto vacío = quitar la variable del .env. */
export interface PedidoConfiguracion {
  corte_mensual?: string;
  corte_diario?: string;
  dir_inputs?: string;
  dir_outputs?: string;
  driver_odbc?: string;
}

export interface EstadoEnvio {
  corte: string;
  prueba: string | null;
  todos: string | null;
  excel: string | null;
}

/** Cambio de usuario y/o contraseña de la web; siempre con la contraseña actual. */
export interface PedidoCuenta {
  clave_actual: string;
  usuario?: string;
  clave_nueva?: string;
}

export interface Sesion {
  usuario: string;
}
