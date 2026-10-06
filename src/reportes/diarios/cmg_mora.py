"""CMG Mora (diario): recaudo + provisiones -> INSERTs para [storage].[com_act].[SBTVRIE001].

Conexión: dw_raw (DW_Raw_v2; dbriesgos por nombre de 3 partes). Ver reportes.config / .env.
"""
import datetime
from datetime import timedelta
import os

from ..config import DIR_OUTPUTS
from ..db import conexion_pyodbc

def generar_inserts_sql():
    # 1. Configuración de conexión y fecha
    # Calcular fecha de ejecución
    hoy = datetime.date.today()
    
    # Regla: si hoy es lunes (0), revisar el sábado (-2 días). Caso contrario, revisar el día anterior (-1 día)
    if hoy.weekday() == 0:  
        fecha_ejec = hoy - timedelta(days=2) 
        print("Hoy es Lunes. Se ejecutará la data correspondiente al Sábado.")
    else:
        fecha_ejec = hoy - timedelta(days=1)
        
    print(f"Fecha actual: {hoy.strftime('%Y-%m-%d')}")
    print(f"Fecha de ejecución objetivo: {fecha_ejec.strftime('%Y-%m-%d')}")
    
    # Formatos de fecha para SQL
    fec_str = fecha_ejec.strftime('%Y-%m-%d')
    fec_tabla = fecha_ejec.strftime('%Y%m%d') # Para buscar PROV_PROY_YYYYMMDD_0
    
    # Ruta de salida
    ruta_salida = DIR_OUTPUTS / 'cmg_mora'
    os.makedirs(ruta_salida, exist_ok=True)
    
    try:
        print("\nConectando a la base de datos SQL Server...")
        # Nos conectamos usando autenticación SQL (sin trusted_connection)
        conn_ctx = conexion_pyodbc('dw_raw')
        conn = conn_ctx.__enter__()
        cursor = conn.cursor()
        
        # ==========================================
        # PARTE 1: Poblado inicial de CMGMora_Recaudo
        # ==========================================
        print("-> Ejecutando PARTE 1 (Carga y tipificación en DW_Raw_v2)...")
        # Se incluye filtro por fecha para traer solo la data del día objetivo
        sql_parte1 = """
        TRUNCATE TABLE DW_Raw_v2.dbo.CMGMora_Recaudo;

        ;WITH recaudo as(
            SELECT 
                CAST(FECHA_CIERRE as date) FECHA_CIERRE
                ,CAST(SALDO as float) SALDO
                ,CAST(RECAUDO as float) RECAUDO
                ,CAST(TASA as float) TASA
                ,CORREDOR ,GRUPO ,TERRITORIO
                ,LTRIM(RTRIM(TERRITORIO))+'-'+LTRIM(RTRIM(GRUPO))+'-'+LTRIM(RTRIM(CORREDOR)) TER_GRU_COR
                ,CASE WHEN CORREDOR IN ('SIN ASIGNAR', 'TOTAL') THEN 20 ELSE 19 END TIP_COD
            FROM dbriesgos.dbo.RECAUDO_DIARIO_FINANZAS
            WHERE CAST(FECHA_CIERRE as date) = ?
        )
        INSERT INTO DW_Raw_v2.dbo.CMGMora_Recaudo
        SELECT
            B.FECHA_CIERRE AS SFECPRO
            ,B.CORREDOR ,B.GRUPO ,B.TERRITORIO
            ,B.TIP_COD AS STIPCOD
            ,J.RCODCOR AS SCODREL
            ,B.RECAUDO AS SMONREC
            ,B.TASA AS STASREC
            ,0 AS SRECCAST12M
            ,0 AS SSTKPROV	
            ,0 AS SGASPROVCART	
            ,0 AS SGASPROVCONTA	
            ,0 AS SGASPROVOM3155	
            ,0 AS SGASPROVVOLU	
            ,0 AS SGASPROVBRUTO	
            ,0 AS SGASPROVBRUTO12M
        FROM recaudo B
        LEFT JOIN DW_Raw_v2.dbo.CMGMora_STRJERCOR J ON (B.TER_GRU_COR=J.[TER-GRU-COR]);

        UPDATE DW_Raw_v2.dbo.CMGMora_Recaudo 
        SET STIPCOD = 7 
        WHERE CORREDOR IN ('TOTAL') AND GRUPO IN ('TOTAL');
        """
        cursor.execute(sql_parte1, fec_str)
        
        # Validar si hubo inserts para esa fecha
        cursor.execute("SELECT COUNT(*) FROM DW_Raw_v2.dbo.CMGMora_Recaudo")
        if cursor.fetchone()[0] == 0:
            print(f"\n[!] ALERTA: No se encontró data en RECAUDO_DIARIO_FINANZAS para la fecha {fec_str}. Abortando.")
            return

        # ==========================================
        # PARTE 2: Actualización y validación de variables (NO CERO)
        # ==========================================
        print("-> Ejecutando PARTE 2 (Cálculo de provisiones)...")
        
        # Asignamos variables estáticas
        sql_update_const = """
        UPDATE DW_Raw_v2.dbo.CMGMora_Recaudo 
        SET 
            SRECCAST12M = 3437395.96
            ,SGASPROVBRUTO12M = 69127536.6
            ,SGASPROVOM3155 = 0
        WHERE STIPCOD = 7;
        """
        cursor.execute(sql_update_const)
        
        tabla_prov = f"[dbriesgos].[dbo].[PROV_PROY_{fec_tabla}_0]"
        
        # Consultamos las variables dinámicas
        # Se hace un bloque TRY CATCH implícito al consultar si la tabla existe
        cursor.execute(f"SELECT OBJECT_ID('{tabla_prov}')")
        if cursor.fetchone()[0] is None:
            print(f"\n[!] ERROR: La tabla {tabla_prov} no existe en la base de datos. Abortando.")
            return
        
        # Extraer los valores
        sql_get_vars = f"""
        SELECT 
            (SELECT ISNULL(SUM(PROVISION_PROYECTADA), 0.0) FROM {tabla_prov}) as SSTKPROV,
            (SELECT ISNULL(SUM(GASTO_OPE), 0.0) FROM [dbriesgos].[dbo].GASTO_PROV_OPE_DIARIA WHERE CAST(FC_DIA as date) = ?) as SGASPROVCART
        """
        cursor.execute(sql_get_vars, fec_str)
        row = cursor.fetchone()
        
        sstkprov = float(row[0]) if row[0] else 0.0
        sgasprovcart = float(row[1]) if row[1] else 0.0
        sgasprovconta = sgasprovcart  # Mismo valor que el de cartera
        
        print(f"   Variables extraídas -> SSTKPROV: {sstkprov:.2f} | SGASPROVCART: {sgasprovcart:.2f}")
        
        # VALIDACIÓN CLAVE: Si están en 0, detenemos el proceso
        if sstkprov == 0.0 or sgasprovcart == 0.0:
            print("\n" + "="*60)
            print("🛑 ADVERTENCIA: Las variables de provisión están en 0.")
            print("🛑 SEGÚN LAS REGLAS, NO SE GENERARÁN LOS INSERTS. ABORTANDO.")
            print("="*60 + "\n")
            return
            
        # Si pasaron la validación (no son 0), actualizamos en SQL
        sql_update_prov = """
        UPDATE DW_Raw_v2.dbo.CMGMora_Recaudo
        SET 
            SSTKPROV = ?
            ,SGASPROVCART = ?
            ,SGASPROVCONTA = ? 
        WHERE STIPCOD = 7
        """
        cursor.execute(sql_update_prov, sstkprov, sgasprovcart, sgasprovconta)
        
        # ==========================================
        # PARTE 3: Extracción y Generación del TXT final
        # ==========================================
        print("-> Extrayendo sentencias INSERT finales (PARTE 3)...")
        sql_select_inserts = """
        SELECT 
            'INSERT INTO [storage].[com_act].[SBTVRIE001] VALUES (' + 
            '''' + CONVERT(VARCHAR(25), SFECPRO, 121) + ''',' + 
            CAST(STIPCOD AS VARCHAR(50)) + ', ' +
            '''' + REPLACE(SCODREL, '''', '''''') + ''', ' +
            CAST(CAST(SMONREC AS DECIMAL(20,7)) AS VARCHAR(50))  + ', ' +
            CAST(CAST(STASREC AS DECIMAL(20,7)) AS VARCHAR(50))  + ', ' +
            CAST(SRECCAST12M AS VARCHAR(50)) + ', ' +    
            CAST(SSTKPROV AS VARCHAR(50)) + ', ' +    
            CAST(SGASPROVCART AS VARCHAR(50)) + ', ' +    
            CAST(SGASPROVCONTA AS VARCHAR(50)) + ', ' +    
            CAST(SGASPROVOM3155 AS VARCHAR(50)) + ', ' +    
            CAST(SGASPROVVOLU AS VARCHAR(50)) + ', ' +    
            CAST(SGASPROVBRUTO AS VARCHAR(50)) + ', ' +    
            CAST(SGASPROVBRUTO12M AS VARCHAR(50)) +    
            ');' AS Inserts
        FROM DW_Raw_v2.dbo.CMGMora_Recaudo;
        """
        cursor.execute(sql_select_inserts)
        inserts = cursor.fetchall()
        
        if not inserts:
            print("\n[!] No se generaron registros en la tabla.")
            return
            
        archivo_txt = os.path.join(ruta_salida, f"inserts_{fec_str}.txt")
        with open(archivo_txt, 'w', encoding='utf-8') as f:
            for fila in inserts:
                f.write(fila[0] + "\n")
                
        print(f"\n✅ [ÉXITO] Se generaron {len(inserts)} registros INSERTS.")
        print(f"✅ [ARCHIVO GUARDADO EN] {archivo_txt}")

    except Exception as e:
        print(f"\n[X] Ocurrió un error en la ejecución SQL o en el proceso: {e}")
    finally:
        if 'conn_ctx' in locals():
            conn_ctx.__exit__(None, None, None)
            print("-> Conexión a la base de datos cerrada de manera segura.")

def main(argv=None) -> int:
    generar_inserts_sql()
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
