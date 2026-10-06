import pandas as pd
import os

def generar_inserts_separados():
    # Rutas a las carpetas proporcionadas
    ruta_recaudo = r'D:\FINANCIERA CONFIANZA\02 TAREAS\01 TAREAS DIARIAS\04 CMG MORA\OCTUBRE\PENDIENTES\RECAUDO'
    ruta_gasto = r'D:\FINANCIERA CONFIANZA\02 TAREAS\01 TAREAS DIARIAS\04 CMG MORA\OCTUBRE\PENDIENTES\GASTO_PROV_OPE_DIARIA'
    
    # Fechas a procesar (01, 02, 03 de octubre)
    fechas = ['01', '02', '03']
    anio_mes = '2026-10' # Ajustar el año/mes según sea necesario
    
    # Variables estáticas basadas en la consulta
    SRECCAST12M_val = 3437395.96
    SGASPROVBRUTO12M_val = 69127536.6
    SGASPROVOM3155_val = 0

    for dia in fechas:
        fecha_str = f'{anio_mes}-{dia}'
        print(f"\n{'='*40}")
        print(f"Procesando fecha: {fecha_str}")
        print(f"{'='*40}")
        
        # 1. Cargar archivo de recaudo para el día
        try:
            archivos_recaudo = [f for f in os.listdir(ruta_recaudo) if dia in f and f.endswith(('.xlsx', '.xls', '.csv'))]
        except Exception as e:
            print(f"Error accediendo a la ruta de recaudo: {e}")
            return

        if not archivos_recaudo:
            print(f"  [!] No se encontró archivo de Recaudo para el día {dia}.")
            continue
            
        ruta_archivo_recaudo = os.path.join(ruta_recaudo, archivos_recaudo[0])
        print(f"  Leyendo recaudo: {archivos_recaudo[0]}")
        
        df_recaudo = pd.read_csv(ruta_archivo_recaudo) if ruta_archivo_recaudo.endswith('.csv') else pd.read_excel(ruta_archivo_recaudo)
        
        # 2. Cargar archivo de gasto operativo para el día
        try:
            archivos_gasto = [f for f in os.listdir(ruta_gasto) if dia in f and f.endswith(('.xlsx', '.xls', '.csv'))]
        except Exception as e:
            print(f"Error accediendo a la ruta de gasto: {e}")
            return
            
        sgasprovcart = 0.0
        sgasprovconta = 0.0
        
        if archivos_gasto:
            ruta_archivo_gasto = os.path.join(ruta_gasto, archivos_gasto[0])
            print(f"  Leyendo gasto: {archivos_gasto[0]}")
            df_gasto = pd.read_csv(ruta_archivo_gasto) if ruta_archivo_gasto.endswith('.csv') else pd.read_excel(ruta_archivo_gasto)
            
            if 'GASTO_OPE' in df_gasto.columns:
                sgasprovcart = float(df_gasto['GASTO_OPE'].sum())
                sgasprovconta = sgasprovcart
        else:
            print(f"  [!] No se encontró archivo de Gasto para el día {dia}. Valores en 0.")
            
        # 3. Tipificación
        df_recaudo['TIP_COD'] = 19
        if 'CORREDOR' in df_recaudo.columns:
            mask_20 = df_recaudo['CORREDOR'].isin(['SIN ASIGNAR', 'TOTAL'])
            df_recaudo.loc[mask_20, 'TIP_COD'] = 20
            
        if 'RCODCOR' not in df_recaudo.columns:
            df_recaudo['SCODREL'] = 'SIN_CODIGO'
        else:
            df_recaudo['SCODREL'] = df_recaudo['RCODCOR']
            
        # 4. Construcción de Tabla
        df_final = pd.DataFrame()
        df_final['SFECPRO'] = [fecha_str] * len(df_recaudo)
        df_final['STIPCOD'] = df_recaudo['TIP_COD']
        df_final['SCODREL'] = df_recaudo['SCODREL']
        df_final['SMONREC'] = df_recaudo['RECAUDO'].fillna(0) if 'RECAUDO' in df_recaudo.columns else 0
        df_final['STASREC'] = df_recaudo['TASA'].fillna(0) if 'TASA' in df_recaudo.columns else 0
        
        df_final['SRECCAST12M'] = 0.0
        df_final['SSTKPROV'] = 0.0 
        df_final['SGASPROVCART'] = 0.0
        df_final['SGASPROVCONTA'] = 0.0
        df_final['SGASPROVOM3155'] = 0.0
        df_final['SGASPROVVOLU'] = 0.0
        df_final['SGASPROVBRUTO'] = 0.0
        df_final['SGASPROVBRUTO12M'] = 0.0
        
        # 5. Lógica de Provisiones
        if 'CORREDOR' in df_recaudo.columns and 'GRUPO' in df_recaudo.columns:
            mask_total = (df_recaudo['CORREDOR'] == 'TOTAL') & (df_recaudo['GRUPO'] == 'TOTAL')
            df_final.loc[mask_total, 'STIPCOD'] = 7
            
        mask_7 = df_final['STIPCOD'] == 7
        df_final.loc[mask_7, 'SRECCAST12M'] = SRECCAST12M_val
        df_final.loc[mask_7, 'SGASPROVBRUTO12M'] = SGASPROVBRUTO12M_val
        df_final.loc[mask_7, 'SGASPROVOM3155'] = SGASPROVOM3155_val
        df_final.loc[mask_7, 'SGASPROVCART'] = sgasprovcart
        df_final.loc[mask_7, 'SGASPROVCONTA'] = sgasprovconta
        
        # 6. Generación de Inserts y Guardado por archivo
        inserts_del_dia = []
        for _, row in df_final.iterrows():
            sfecpro_formatted = f"{row['SFECPRO']} 00:00:00.000"
            insert_stmt = (
                f"INSERT INTO [storage].[com_act].[SBTVRIE001] VALUES ("
                f"'{sfecpro_formatted}', {row['STIPCOD']}, '{row['SCODREL']}', "
                f"{row['SMONREC']:.7f}, {row['STASREC']:.7f}, "
                f"{row['SRECCAST12M']}, {row['SSTKPROV']}, {row['SGASPROVCART']}, "
                f"{row['SGASPROVCONTA']}, {row['SGASPROVOM3155']}, {row['SGASPROVVOLU']}, "
                f"{row['SGASPROVBRUTO']}, {row['SGASPROVBRUTO12M']});"
            )
            inserts_del_dia.append(insert_stmt)
            
        if inserts_del_dia:
            # Crea un archivo txt distinto para cada día
            nombre_archivo = f'inserts_{fecha_str}.txt'
            ruta_salida = os.path.join(ruta_recaudo, nombre_archivo)
            try:
                with open(ruta_salida, 'w', encoding='utf-8') as f:
                    for inst in inserts_del_dia:
                        f.write(inst + '\n')
                print(f"  [EXITO] Se generaron {len(inserts_del_dia)} INSERTS.")
                print(f"  [GUARDADO EN] {ruta_salida}")
            except Exception as e:
                print(f"  Error guardando los inserts: {e}")

if __name__ == '__main__':
    generar_inserts_separados()
