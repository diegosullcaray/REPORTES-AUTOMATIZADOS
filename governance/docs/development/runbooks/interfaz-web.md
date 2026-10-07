# Interfaz web

Gestiona los reportes desde el navegador con el mismo procedimiento que la consola. Decisión: [ADR-0011](../../architecture/adr/ADR-0011-interfaz-web.md).

## Arrancar (dos terminales)

```bat
:: 1) API (entorno activado, .env completo)
env\Scripts\activate
pip install -r requirements.txt
python -m uvicorn api.app:app --app-dir src --host 127.0.0.1 --port 8000

:: 2) Web (Node 20+)
cd web
npm install
npm run build && npm start        :: o `npm run dev` mientras desarrollas
```

Abre http://localhost:3000. Si la API corre en otro puerto: `set REPORTES_API_URL=http://127.0.0.1:PUERTO` antes de `npm start`.
Si cambias el `.env`, reinicia la API (lo lee al arrancar).

## Procedimiento por reporte

Elige el reporte en el **panel de reportes** junto al rail (agrupado en Diarias, Piero y Erick, con buscador).
En el celular ese panel es la pantalla de lista y el reporte se abre a pantalla completa.

| Paso | Pestaña | Qué hace | Equivale a |
|---|---|---|---|
| 1 | Validar tablas | Fecha de corte → **Verificar tablas** (solo SELECT). Si falta alguna: mensaje para Producción, **Copiar** o **Guardar** en `data/outputs/solicitudes/` | `tablas <r> --verificar` · `solicitud-actualizacion` |
| 2 | Ejecutar | Lista de control (fecha válida, tablas al día, confirmaciones) → **Ejecutar** → confirmación → cola | `python main.py <r> --fecha-corte …` |
| 3 | Archivos | Excel, imagen y textos de la carpeta del reporte, con **vista previa** (200 filas por hoja) y descarga | `data/outputs/<…>/` |
| 4 | Correo (solo `cartera-sin-asignar`) | Estado de la prueba; **Enviar a toda la lista** exige marcar «Revisé el correo de prueba» | `--correo todos --conforme` |
| — | Historial | Ejecuciones del reporte con su log | — |

Reglas que la API exige (aunque la web ya las avise):

- Mensual = fin de mes; ninguna fecha de corte en el futuro.
- `tapp-saldo-medio-territorio` exige confirmar la escritura en BD.
- `--forzar` solo aparece si la verificación encontró tablas desactualizadas, y queda escrito en el historial.
- Enviar a todos exige una prueba previa del mismo corte y el conforme; no reenvía si ya se envió.
- Un reporte a la vez: los demás esperan **En cola**.

## Estados de una ejecución

| Estado | Código | Qué hacer |
|---|---|---|
| Correcto | 0 | Revisa los archivos generados (vista previa en la misma página) y entrégalos |
| Error | 1 | Lee la salida: datos vacíos, Excel abierto, error SQL |
| Configuración | 2 | Fecha, `.env`, driver o confirmación faltante |
| Tablas desactualizadas | 3 | Paso 1: pide la carga a Producción y vuelve a verificar |

Si la API se reinicia con una ejecución en curso, queda en **Error** con la nota «Interrumpida».

## Estructura

```text
src/api/            app.py (rutas) · esquemas.py (contratos) · servicios.py (casos de uso) · ejecuciones.py (cola)
web/src/app/        rutas: /reportes (layout con el sidebar secundario del catálogo) · /reportes/[nombre] · /ejecuciones · /ejecuciones/[id] · /conexiones; tokens.css (copia de MIS)
web/src/lib/        api.ts (transporte) · tipos.ts (espejo de esquemas.py) · formato.ts (funciones puras)
web/src/features/   orquestación por pantalla (reportes, ejecuciones, conexiones)
web/src/components/ presentación compartida: ventana, shell, estados (error · cargando · vacío), confirmar; ui/ = shadcn
```
