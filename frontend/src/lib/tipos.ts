// Espejo de src/modulos/<módulo>/aplicacion/dto.py. Si cambia un contrato allá, se cambia aquí.

/** Id de un grupo de reportes: diarias, piero, erick o uno creado desde la web. */
export type Grupo = string;

/** Etiqueta (como los tags de Dokploy): nombre y color #rrggbb que elige la persona, para organizar los grupos. */
export interface Etiqueta {
  id: string;
  nombre: string;
  color: string;
}

export interface GrupoReportes {
  id: Grupo;
  nombre: string;
  frecuencia: Frecuencia;
  propio: boolean;
  reportes: number;
  etiquetas: Etiqueta[];
}
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
  /** Puede enviar su archivo por Google Chat (--chat). */
  envia_chat: boolean;
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
  /** A quién se envía el archivo por Google Chat (ENTREGA_CHAT_<REPORTE> del .env). */
  chat_destinatarios: string[];
  /** Destinatarios y copia del correo con los archivos (ENTREGA_CORREO_PARA_/CC_<REPORTE> del .env). */
  correo_para: string[];
  correo_cc: string[];
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

/** Una verificación del grupo guardada en el historial (resumen por reporte; sin el detalle por tabla). */
export interface EntradaValidacion {
  id: string;
  grupo: string;
  ejecutada: string;
  corte: string;
  listo: boolean;
  reportes: ResumenValidacion[];
  tablas_total: number;
  tablas_ok: number;
  tablas_pendientes: number;
  tablas_dudosas: number;
  solicitud: string | null;
  chat_enviado: string | null;
  chat_a: string[];
}

export interface DestinosChat {
  destinatarios: string[];
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
  chat?: boolean;
  fase?: "operaciones" | "provisiones" | "generar"; // solo cmg-mora
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

export interface PedidoReporteNuevo {
  nombre: string;
  grupo: Grupo;
  orden: string;
  descripcion: string;
  sql?: string;
}

export interface ReporteCreado {
  nombre: string;
  ruta: string;
  tablas_nuevas: string[];
}

export interface Script {
  ruta: string;
  codigo: string;
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

export interface PedidoEnvioArchivos {
  para: string[];
  cc: string[];
  asunto: string;
  mensaje: string;
  archivos: string[];
  con_firma: boolean;
  prueba: boolean;
}

export interface FirmaGmail {
  html: string; // vacío si la cuenta no tiene firma
}

export interface PruebaNotificacion {
  ok: boolean;
  detalle: string;
}

export interface HerramientaMcp {
  nombre: string;
  descripcion: string;
}

export interface ServicioGoogle {
  id: string;
  nombre: string;
  /** Servidor MCP oficial de Google. */
  url: string;
  activo: boolean;
  /** Además, envío directo por la API (Gmail, Chat). */
  envia: boolean;
  scopes: string[];
  /** Activo, pero el token no tiene sus permisos: hay que volver a autorizar. */
  falta_consentimiento: boolean;
}

/** MCP de Google Workspace. El Client secret y el token nunca llegan al navegador: solo si están configurados. */
/** Conexión con un proveedor de IA por API key (la clave nunca llega al navegador). */
export interface ConfigIA {
  id: string;
  nombre: string;
  api_url: string;
  modelo: string;
  activo: boolean;
  proveedor: string;
  clave_configurada: boolean;
}

export interface PedidoIA {
  nombre: string;
  api_url: string;
  api_key: string;
  modelo: string;
  activo: boolean;
}

export interface ModelosIA {
  proveedor: string;
  modelos: string[];
}

export interface GoogleMcp {
  client_id: string;
  secreto_configurado: boolean;
  redirect_uri: string;
  cuenta: string;
  autorizado: boolean;
  correo_prueba: string;
  servicios: ServicioGoogle[];
  herramientas_envio: HerramientaMcp[];
  python: string;
  configuracion: Record<string, unknown>;
}

/** Solo se envían los campos cambiados; texto vacío = quitar la variable del .env. */
export interface PedidoGoogleMcp {
  client_id?: string;
  client_secret?: string;
  redirect_uri?: string;
  cuenta?: string;
  servicios?: string[];
}

export interface HerramientaRemota {
  nombre: string;
  descripcion: string;
  esquema: { properties?: Record<string, { type?: string; description?: string }>; required?: string[] };
}

export interface PruebaMcp {
  ok: boolean;
  detalle: string;
  herramientas: HerramientaRemota[];
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

// ---- Diccionario de datos (módulo diccionario del backend)
export interface DicHallazgo { nivel: string; regla: string; origen: string; objeto: string; detalle: string; en_linea_base: boolean }
export interface DicBase { base: string; procedimientos: number; extraidos: number; validados: number; tablas: number }
export interface DicResumen {
  carpeta: string; generado: string; reportes: number; procedimientos: number; extraidos: number; validados: number; tablas: number; columnas: number;
  errores: number; avisos: number; errores_nuevos: number; bases: DicBase[];
}
export interface DicBaseFila { base: string; procedimientos: number; validados: number; reportes: number; tablas_propias: number; tablas_usadas: number }
export interface DicProcedimientoFila { nombre: string; estado: string; reportes: string[]; parametros: number; tablas: number }
export interface DicTablaDeBase { nombre: string; base: string; tipo: string | null; existe: boolean | null; columnas: number; propia: boolean; usada_por: number; en_registro: boolean }
export interface DicBaseDetalle { base: string; procedimientos: DicProcedimientoFila[]; tablas: DicTablaDeBase[] }
export interface DicReporteFila { codigo: string; descripcion: string; procedimiento: string; base: string; estado: string; parametros: number; tablas: number; front: string[] }
export interface DicParametro { nombre: string; tipo: string | null; por_defecto: string | null; salida: boolean }
export interface DicColumnaUso { nombre: string; confianza: string | null; es_fecha: boolean }
export interface DicTablaUso { nombre: string; usos: string[]; columnas: DicColumnaUso[] }
export interface DicProcedimiento { nombre: string; base: string; estado: string; parametros: DicParametro[]; resultados: string[][]; invoca: string[]; tablas: DicTablaUso[] }
export interface DicReporteDetalle extends DicReporteFila { parametros_catalogo: string[]; procedimiento_detalle: DicProcedimiento | null; hallazgos: DicHallazgo[] }
export interface DicRegistroTabla { tipo: string; col_fecha: string | null; confianza: string; reportes: string[] }
export interface DicTablaFila { nombre: string; base: string; tipo: string | null; existe: boolean | null; columnas: number; procedimientos: number; en_registro: boolean }
export interface DicColumna { nombre: string; tipo: string | null; acepta_nulos: boolean | null; confianza: string | null; es_fecha: boolean; procedimientos: string[] }
export interface DicTablaDetalle extends DicTablaFila { descripcion: string | null; ficha: string | null; columnas_detalle: DicColumna[]; reportes_mis: string[]; registro: DicRegistroTabla | null }
export interface DicSugerenciaFecha { tabla: string; actual: string | null; confianza: string; motivo: string; candidatas: string[] }
export interface DicTablaDisponible { nombre: string; reportes_mis: number; columnas: number; fechas: string[] }
export interface DicPotencial { tablas_registradas: number; en_diccionario: number; faltan_en_diccionario: string[]; fechas: DicSugerenciaFecha[]; disponibles: DicTablaDisponible[] }
export interface DicProceso { id: string; nombre: string; descripcion: string; comando: string; escribe: string }
export interface DicEjecucion { id: string; proceso: string; estado: "ejecutando" | "ok" | "error"; inicio: string; fin: string | null; codigo: number | null }
export interface DicEjecucionDetalle extends DicEjecucion { log: string }
