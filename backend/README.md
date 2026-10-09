# Backend — motor de reportes y API

Reportes de Financiera Confianza en Python, **ejecutados por ti bajo demanda** (no hay tareas programadas ni procesos en segundo plano).

Con un solo comando el reporte: se conecta a SQL Server → **comprueba que las tablas lleguen al corte** → consulta → valida los datos → exporta el Excel. Si falta cargar alguna tabla, **no se ejecuta**, te dice cuál es y te deja listo el mensaje para pedírsela a Producción.

```bash
python main.py saca-tu-garra          # un reporte, con la fecha de corte de tu .env
```

**¿Prefieres el navegador?** La [interfaz web](../frontend/README.md) hace lo mismo (validar tablas, ejecutar, vista previa del Excel, correo) sobre este mismo motor.

> **Dónde se trabaja:** todos los comandos de este README (`python main.py …`, `env\Scripts\activate`) se ejecutan **dentro de `backend/`**; las rutas `data\…` y `.env` son las de esta carpeta. La web está en [`../frontend`](../frontend/README.md).

> **Regla que manda sobre todo:** cuando la documentación y el código discrepan, gana el código y se corrige el documento. Reglas del repositorio: [AGENTS.md](../AGENTS.md).

---

## Contenido

1. [Qué necesitas](#1-qué-necesitas)
2. [Instalación paso a paso (primera vez)](#2-instalación-paso-a-paso-primera-vez)
3. [Configurar el `.env`](#3-configurar-el-env)
4. [Comprobar que todo funciona](#4-comprobar-que-todo-funciona)
5. [API de la web](#5-api-de-la-web)
6. [Ejecutar un reporte (el flujo de cada vez)](#6-ejecutar-un-reporte-el-flujo-de-cada-vez)
7. [Cierre de mes](#7-cierre-de-mes)
8. [Reportes disponibles](#8-reportes-disponibles)
9. [Qué se genera y dónde](#9-qué-se-genera-y-dónde)
10. [Si algo falla](#10-si-algo-falla)
11. [Qué tener siempre en cuenta](#11-qué-tener-siempre-en-cuenta)
12. [Estructura del proyecto](#12-estructura-del-proyecto)
13. [Guías (mapa de la documentación)](#13-guías-mapa-de-la-documentación)
14. [Si vas a modificar o crear un reporte](#14-si-vas-a-modificar-o-crear-un-reporte)

---

## 1. Qué necesitas

| Requisito | Detalle |
|---|---|
| Sistema | Windows con acceso a la red de la empresa (VPN si estás fuera) |
| Python | **3.11 o superior** (se probó con 3.13) |
| Driver ODBC | **ODBC Driver 17 for SQL Server** (si usas otro, defínelo con `DB_ODBC_DRIVER` en el `.env`) |
| Accesos | Autenticación de Windows en `MISHWBDDES01` (MISH) y `172.24.2.213` (SLC); usuario/contraseña SQL en `172.20.0.70` (RCC). **Los 3 se usan**: el reporte elige el servidor según las bases que consulta |
| Excel cerrado | Los reportes escriben archivos `.xlsx`: si el archivo está abierto, falla al guardar |

Los 3 servidores (cada reporte elige **su propia base de datos** dentro del servidor):

| Conexión | Servidor | Autenticación | Bases que usan los reportes |
|---|---|---|---|
| `mish` | `MISHWBDDES01` | Windows | **`storage`** (cartera, castigos, saldos, captaciones, seguros, fondeo…) y `appj` |
| `slc` | `172.24.2.213` | Windows | `dwh`, `dma`, `csd`, `intcom`, `slc` (clientes, desembolsos, productos) |
| `rcc` | `172.20.0.70` | SQL (usuario `master`) | `dbriesgos`, `DBRCC`, `DW_Raw_v2`, `DW_Metadata`, `DB<AAAAMM>` (CMG Mora, bancarizados) |

**Regla:** una consulta solo puede nombrar bases de **su** servidor; por eso cada reporte se conecta al servidor de las bases que usa (se valida automáticamente). Mapa completo de bases por servidor: [servidores y bases](../governance/docs/data/servidores-y-bases.md).

---

## 2. Instalación paso a paso (primera vez)

Todos los comandos se escriben en una terminal dentro de la carpeta `backend/` del proyecto.

```bat
:: 1) Entra a la carpeta del motor
cd "D:\FINANCIERA CONFIANZA\02 TAREAS\05 TAREAS-AUTOMATIZADAS\backend"

:: 2) Crea el entorno virtual (se llama "env"; ya está en .gitignore)
python -m venv env

:: 3) Actívalo (verás (env) al inicio de la línea)
env\Scripts\activate

:: 4) Instala las dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt        :: solo si vas a correr las pruebas

:: 5) Crea tu archivo de configuración a partir de la plantilla
copy .env.example .env
```

Después edita `.env` (siguiente sección). **Cada vez** que abras una terminal nueva debes activar el entorno otra vez: `env\Scripts\activate`.

Comprueba que Python ve el driver ODBC:

```bat
python -c "import pyodbc; print([d for d in pyodbc.drivers() if 'SQL Server' in d])"
```
Debe listar `ODBC Driver 17 for SQL Server`. Si sale vacío, instala el driver (descarga de Microsoft) y vuelve a probar.

---

## 3. Configurar el `.env`

El `.env` es **tu archivo local** (no se sube a git). Se copia de `.env.example` y tiene tres bloques:

```ini
# 1. MISH  (Windows)
MISH_SERVER=MISHWBDDES01
MISH_USER=
MISH_PASSWORD=

# 2. SLC  (Windows)
SLC_SERVER=172.24.2.213
SLC_USER=
SLC_PASSWORD=

# 3. RCC  (SQL)
RCC_SERVER=172.20.0.70
RCC_USER=master
RCC_PASSWORD=<la contraseña va SOLO aquí>

# Fecha de corte (AAAA-MM-DD)
FECHA_CORTE_MENSUAL=2026-09-30
FECHA_CORTE_DIARIA=

# Interfaz web (opcionales)
# WEB_USUARIO=admin              usuario para entrar a la web (sin él y WEB_CLAVE, nadie entra)
# WEB_CLAVE=                     clave de la web (solo aquí)
# SESION_SECRETO=                firma de la cookie de sesión (vacío = se genera en cada arranque)

# Opcionales
# REPORTES_DIR_INPUTS=D:\FINANCIERA CONFIANZA\data\inputs
# REPORTES_DIR_OUTPUTS=D:\FINANCIERA CONFIANZA\data\outputs

# Correo (solo reporte cartera-sin-asignar; ver su runbook)
SMTP_USER=mis@confianza.pe
SMTP_PASSWORD=<contraseña de aplicación>
CORREO_PRUEBA=diego.sullcaray@confianza.pe
GOOGLE_CHAT_WEBHOOK_URL=<webhook>
```

**Conexiones**
- `*_USER` y `*_PASSWORD` **vacíos** ⇒ autenticación de Windows (válido para `mish` y `slc`).
- `rcc` exige usuario y contraseña SQL. Si pones solo uno de los dos, da error.
- **No hay base de datos en el `.env`**: la base la elige cada reporte. Detalle: [contrato de conexiones](../governance/docs/data/contracts/conexiones-bd.md).
- La contraseña nunca va en el código, en capturas de pantalla ni en el repositorio.

**Fecha de corte**
- `FECHA_CORTE_MENSUAL`: último día del mes a reportar (si cae feriado, el día hábil anterior). **Cámbiala cada mes antes de ejecutar.**
- `FECHA_CORTE_DIARIA`: opcional. Si la dejas vacía, los reportes diarios usan el día anterior (el lunes, el sábado).
- Prioridad: `--fecha-corte AAAA-MM-DD` en el comando **>** `.env` **>** (solo diarios) día anterior. Un reporte mensual sin ninguna fecha se detiene y te lo dice.
- Cada reporte imprime al inicio `Fecha de corte: … (de dónde salió)`. **Confírmala siempre.**

---

## 4. Comprobar que todo funciona

```bat
python main.py listar                 :: lista los 21 reportes (no se conecta)
python main.py probar-conexiones      :: prueba los 3 servidores
python ..\governance\scripts\verificar.py   :: compuertas del repo (no se conecta a ninguna BD)
```

`probar-conexiones` debe mostrar `OK` en los servidores que vayas a usar. Mensajes típicos: ver [Si algo falla](#10-si-algo-falla).

---

## 5. API de la web

La [interfaz web](../frontend/README.md) consume una API (FastAPI, `src/api/`) que vive en este backend. Se arranca desde `backend/`, con el entorno activado y el `.env` completo (si cambias el `.env`, reinicia la API):

```bat
env\Scripts\activate
python -m uvicorn api.app:app --app-dir src --host 127.0.0.1 --port 8000
```

Escucha solo en `127.0.0.1`. Toda la API exige sesión; las credenciales están en el `.env`:

| Variable | Efecto |
|---|---|
| `WEB_USUARIO` | usuario para entrar a la web (no distingue mayúsculas) |
| `WEB_CLAVE` | clave de la web. Si falta alguna de las dos, **nadie puede entrar** |
| `SESION_SECRETO` | firma de la cookie. Vacío = se genera en cada arranque y las sesiones caen al reiniciar la API |

La sesión dura 8 horas; tras 5 intentos fallidos el usuario queda bloqueado 5 minutos. Contrato de rutas y reglas: `src/api/app.py` y `src/api/servicios.py`.

---

## 6. Ejecutar un reporte (el flujo de cada vez)

Los 6 pasos son iguales para todos los reportes. Guía completa: [ejecutar un reporte](../governance/docs/development/runbooks/ejecutar-un-reporte.md).

```bat
:: 0) activa el entorno y revisa la fecha de corte en el .env
env\Scripts\activate

:: 1) ¿qué tablas usa y están al día al corte?   (solo consulta, no modifica nada)
python main.py tablas saca-tu-garra --verificar

:: 2) si alguna salió DESACTUALIZADA o NO EXISTE: genera el mensaje para Producción
python main.py solicitud-actualizacion saca-tu-garra --verificar

:: 3) con todo OK, ejecuta el reporte
python main.py saca-tu-garra

:: 4) valida y entrega el Excel de data\outputs\mensuales\piero\06_saca_tu_garra\
```

**Qué hace el reporte al ejecutarse**
1. Muestra la fecha de corte y de dónde salió.
2. Verifica las tablas al corte. Si falta alguna: **no ejecuta**, lista cuáles faltan y guarda el mensaje en `data\outputs\solicitudes\` (código de salida 3).
3. Ejecuta el T-SQL en una sola sesión.
4. Valida los datos: todo vacío ⇒ error (salvo reportes donde vacío es válido, como Castigos); resultado con fecha anterior al corte ⇒ error.
5. Exporta el Excel con el **formato del legado** (una hoja por resultado, solo los datos; sin hoja de control). Nombres de archivo y hojas: [formato Excel](../governance/docs/data/formato-excel.md).

**Opciones que tienen todos los reportes de lote**

| Opción | Para qué |
|---|---|
| `--fecha-corte AAAA-MM-DD` | usa esa fecha solo esta vez (manda sobre el `.env`) |
| `--solo-verificar` | solo valida tablas y genera el mensaje; no ejecuta |
| `--forzar` | ejecuta aunque haya tablas desactualizadas (se avisa en pantalla; úsalo bajo tu responsabilidad) |
| `--sin-verificar` | no valida tablas (no recomendado) |
| `--confirmar-escritura` | obligatorio en reportes que crean/borran tablas permanentes (`tapp-saldo-medio-territorio`) |
| `--salida CARPETA` | cambia la carpeta de salida |
| `-v` | detalle de log |

Los 5 reportes con lógica propia (`cmg-mora`, `bancarizados`, `bancarizados-producto`, `clientes-extranjeros`, `indicadores-clientes`) tienen sus propias opciones: `python main.py <reporte> --help` y su [runbook](../governance/docs/development/runbooks/README.md).

**Cartera sin asignar (diario) además envía correo**: por defecto manda una **prueba solo a tu correo**; con tu conforme: `python main.py cartera-sin-asignar --correo todos --conforme` (guía: [runbook](../governance/docs/development/runbooks/cartera-sin-asignar.md)).

**Códigos de salida de los reportes de lote:** `0` correcto · `1` error de datos o de ejecución · `2` configuración (`.env`, driver, fecha) · `3` tablas desactualizadas.

---

## 7. Cierre de mes

Procedimiento completo, con el orden sugerido de reportes y las tablas que suelen retrasar el cierre: [proceso de cierre de mes](../governance/docs/development/runbooks/proceso-cierre-de-mes.md). Resumen:

1. En el `.env`: `FECHA_CORTE_MENSUAL=AAAA-MM-DD` (fin de mes).
2. `python main.py probar-conexiones`.
3. Para cada reporte mensual: `python main.py tablas <reporte> --verificar`.
4. Junta todas las tablas desactualizadas y haz **una sola** solicitud a Producción ([cómo pedirlo](../governance/docs/development/runbooks/solicitud-actualizacion-tablas.md)). El [inventario de tablas](../governance/docs/data/tables-inventory.md) (sección «por tabla») te dice qué otros reportes se destraban con cada tabla.
5. Cuando Producción confirme, **vuelve a verificar** (no asumas que ya cargó) y ejecuta cada reporte.
6. Entrega a los destinatarios según el [catálogo de reportes](../governance/docs/business/domain-catalog.md) (el envío por correo es manual).

---

## 8. Reportes disponibles

`python main.py listar` muestra la lista actual, **en el orden y con la numeración de las carpetas del legado**. Catálogo completo (tablas críticas, salida, avisos): [catálogo de comandos](../governance/docs/development/runbooks/comandos.md).

| Nº | Diarias («01 TAREAS DIARIAS») | Comando |
|---|---|---|
| 02 | Cartera sin asignar (genera Excel + imagen y **envía por correo**: prueba → conforme → todos) | `cartera-sin-asignar` |
| 04.1 | CMG Mora | `cmg-mora` |

| Nº | Mensuales · heredados de **Piero** | Comando |
|---|---|---|
| 01 | Desembolsos por canal | `desembolsos-por-canal` |
| 02 | Estadística de tramo - Fondeo estable | `fondeo-estable` |
| 03 | Heredados PDM | `heredados-pdm` *(pendiente de definir su formato)* |
| 04.1 / 04.2 | Ratio CE, clientes nuevos y migrantes | `contratacion-electronica`, `clientes-rurales-migrantes` |
| 05.1 / 05.2 / 05.3 | Reportes para Giovanni | `giovanni-captaciones`, `giovanni-seguros`, `giovanni-cartera-agro` |
| 06 | Saca tu garra | `saca-tu-garra` |
| 07 | Saldo medio vigente | `saldo-medio-vigente` |
| 08 | TAPP stock TPP mes saldo medio vigente territorio | `tapp-saldo-medio-territorio` |
| 09.1 / 09.2 | Reporte mensual Michael Palacios | `michael-captaciones`, `michael-castigos` |

| Nº | Mensuales · heredados de **Erick** | Comando |
|---|---|---|
| 01 | Productos verdes | `productos-verdes` |
| 02 | Clientes jóvenes | `clientes-jovenes` |
| 03.1 – 03.4 | Clientes exclusivos, desempeño social (Reporte Finanzas) | `bancarizados`, `bancarizados-producto`, `clientes-extranjeros`, `indicadores-clientes` |

---

## 9. Qué se genera y dónde

Las salidas siguen la misma numeración del legado:

| Ruta | Contenido | ¿Se sube a git? |
|---|---|---|
| `data\outputs\mensuales\piero\<NN_nombre>\` | reportes mensuales heredados de Piero (p. ej. `01_desembolsos_por_canal\Desembolsos_canal_20260930.xlsx`, `06_saca_tu_garra\Base Saca tu Garra_20260930.xlsx`) | No |
| `data\outputs\mensuales\erick\<NN_nombre>\` | reportes mensuales heredados de Erick (p. ej. `01_productos_verdes\7. Productos_verdes_sep26.xlsx`) | No |
| `data\outputs\diarias\<NN_nombre>\` | reportes diarios (p. ej. `02_cartera_sin_asignar\Cartera-Sin asignar-2026-10-05.xlsx`, la imagen `Reporte_Temporal_…jpg` y el estado del envío) | No |
| `data\outputs\solicitudes\` | mensajes para Producción (`solicitud_<reporte>_<AAAAMMDD>.txt`) | No |
| `data\inputs\` | archivos de entrada (Excel base y la lista de correos `correos_cartera_sin_asignar.txt`) | solo la estructura y la lista de correos |

Con `REPORTES_DIR_OUTPUTS=D:\FINANCIERA CONFIANZA\02 TAREAS\05 TAREAS-AUTOMATIZADAS\data\outputs` las salidas mensuales quedan en `…\data\outputs\mensuales`.
Los archivos contienen **datos de clientes**: no los subas al repositorio ni los compartas fuera de los destinatarios autorizados.

---

## 10. Si algo falla

| Mensaje | Causa | Qué hacer |
|---|---|---|
| `Falta el driver ODBC / pyodbc` | no está el driver 17 o el entorno no tiene `pyodbc` | instala el driver; activa `env` y `pip install -r requirements.txt` |
| `La conexión rcc requiere RCC_USER y RCC_PASSWORD` | falta usuario/contraseña de `rcc` en el `.env` | complétalos (solo en tu `.env`) |
| `Falta la fecha de corte mensual: … FECHA_CORTE_MENSUAL` | no hay fecha en `.env` ni `--fecha-corte` | escribe `FECHA_CORTE_MENSUAL=AAAA-MM-DD` |
| `FECHA_CORTE_… en el .env no es válida` | formato distinto de `AAAA-MM-DD` | corrígelo (ej. `2026-09-30`) |
| `La fecha de corte debe ser fin de mes` | un reporte mensual recibió otro día | usa el último día del mes (feriado: día hábil anterior) |
| `✗ N tabla(s) sin actualizar al corte` (código 3) | Producción aún no cargó el cierre | usa el mensaje de `data\outputs\solicitudes\`; reverifica; no uses `--forzar` salvo que lo decidas |
| `No pude verificar ninguna tabla` | conexión caída o sin permisos | `python main.py probar-conexiones`; revisa VPN y credenciales |
| `AVISO: no pude verificar <tabla> … confirma su columna de fecha` | la columna de fecha de esa tabla es una inferencia | confírmala con el DBA y corrígela en `src/reportes/tablas.py` |
| `✗ Datos: Todos los resultados vinieron vacíos` | casi seguro falta cargar una tabla al corte | `python main.py tablas <reporte> --verificar` |
| `✗ Datos: … llega solo hasta <fecha>, antes del corte` | tabla desactualizada | pide la actualización |
| `… crea/borra tablas permanentes … --confirmar-escritura` | el reporte escribe en BD | repite con `--confirmar-escritura` solo si estás seguro |
| `No sé en qué servidor vive la base '…'` | base nueva sin mapear | añádela a `BASES_DE` en `src/reportes/config.py` |
| `Invalid object name` / `database … does not exist` | el reporte se conecta a un servidor que no tiene esa base | revisa que `servidor` y `base` del reporte coincidan con [servidores y bases](../governance/docs/data/servidores-y-bases.md) |
| `PermissionError` al exportar | el Excel de salida está abierto | ciérralo y repite |
| `Error de base de datos al ejecutar …` | error SQL o de red | repite con `-v` y revisa el detalle |

Más contexto: [solicitud de actualización de tablas](../governance/docs/development/runbooks/solicitud-actualizacion-tablas.md) y [registro de incidentes](../governance/docs/evidence/quality/incidents.md).

---

## 11. Qué tener siempre en cuenta

1. **Nunca ejecutes con tablas `DESACTUALIZADA`:** el resultado sale plausible y equivocado.
2. **Confirma la fecha de corte** impresa al inicio. Es lo primero que se olvida al cambiar de mes.
3. **Secretos solo en el `.env`.** Jamás en código, SQL, documentos, capturas o chats. Las credenciales que aparecen en `docs/LEGADO` siguen pendientes de rotar ([hallazgo SEC-001](../governance/docs/security/findings.md)).
4. **`rcc` se usa con el usuario `master`** (lectura y escritura). Cuidado con lo que ejecutas ahí; el plan es un usuario de mínimo privilegio ([SEC-002](../governance/docs/security/findings.md)).
5. **`cmg-mora` escribe** en `DW_Raw_v2` (trunca `CMGMora_Recaudo`): no lo ejecutes dos veces a la vez. Se detiene si las provisiones son 0.
6. **`tapp-saldo-medio-territorio` crea y borra** la tabla permanente `appj.dbo.salmediovigente1`: exige `--confirmar-escritura`.
7. **Vacío no es error y error no es vacío.** `michael-castigos` puede salir vacío (hay meses sin castigos); `michael-captaciones` no.
8. **Los nombres de hoja** de varios reportes son `Resultado_1`, `Resultado_2`… hasta fijarlos tras la primera ejecución real.
9. **Primera ejecución real de cada reporte:** compárala con la salida manual del mes anterior antes de entregarla. La lógica se migró desde `docs/LEGADO` con fechas parametrizadas, pero no se ha probado contra las bases reales desde el entorno de desarrollo ([ADR-0005](../governance/docs/architecture/adr/ADR-0005-reportes-como-modulos-py.md)).
10. **`docs/LEGADO` es solo lectura** (archivo histórico). No lo edites ni lo uses para ejecutar.
11. **Excel cerrado** antes de ejecutar; los archivos de `data\` no se versionan.
12. **Entrega por correo:** manual. Destinatarios y formato: [procedimientos heredados](../governance/docs/business/procedimientos_manuales_legado.md).

---

## 12. Estructura del proyecto

```text
main.py                       punto de entrada único (listar | probar-conexiones | tablas | solicitud-actualizacion | <reporte>)
.env.example                  plantilla del .env (el .env real no se versiona)
requirements*.txt             dependencias (dev = pytest)
env/                          entorno virtual (no versionado)
src/reportes/
  config.py                   rutas, los 3 servidores y carpetas data/
  db.py                       ÚNICO acceso a SQL Server (servidor + base por reporte)
  registro.py                 catálogo de reportes
  tablas.py                   tablas de cada reporte (servidor, tipo, columna de fecha)
  verificacion.py             ¿tablas al día? + mensaje para Producción
  comun/ejecutor.py           flujo común: conexión → tablas → consulta → validación → Excel
  comun/fechas.py             fecha de corte (.env / --fecha-corte) y tokens @@F@@…
  comun/excel.py              formato Excel del legado (tabla, resumen jerárquico, columnas)
  comun/imagen.py correo.py   imagen del resumen y envío por correo (cuenta MIS)
  diarios/                    r02_cartera_sin_asignar.py, r04_1_cmg_mora.py … (número del legado)
  mensuales/piero/            r01_desembolsos_por_canal.py … r09_2_michael_castigos.py
  mensuales/erick/            r01_productos_verdes.py … r03_4_indicadores_clientes.py
src/api/                      API de la web (FastAPI): rutas, servicios, ejecuciones y sesión
data/inputs/  data/outputs/   entradas y salidas locales (no versionadas)
tests/                        pytest (no tocan las bases reales)
```

`governance/` y `docs/LEGADO/` están en la raíz del repositorio, un nivel arriba.

---

## 13. Guías (mapa de la documentación)

Todo está en [`governance/`](../governance/readme.md). Lo que más vas a usar:

| Necesito… | Lee |
|---|---|
| Ejecutar cualquier reporte | [Ejecutar un reporte](../governance/docs/development/runbooks/ejecutar-un-reporte.md) |
| Hacer el cierre de mes | [Proceso de cierre de mes](../governance/docs/development/runbooks/proceso-cierre-de-mes.md) |
| Saber qué hace cada comando | [Catálogo de comandos](../governance/docs/development/runbooks/comandos.md) |
| Pedir una tabla a Producción | [Solicitud de actualización](../governance/docs/development/runbooks/solicitud-actualizacion-tablas.md) |
| Ver qué tabla usa cada reporte | [Inventario de tablas](../governance/docs/data/tables-inventory.md) |
| Guía de un reporte concreto | [Runbooks](../governance/docs/development/runbooks/README.md) |
| Entender las conexiones y bases | [Contrato de conexiones](../governance/docs/data/contracts/conexiones-bd.md) |
| Quién pide cada reporte | [Catálogo de reportes](../governance/docs/business/domain-catalog.md) |
| Primer día en el proyecto | [Onboarding](../governance/docs/onboarding.md) · [Setup](../governance/docs/development/setup-guide.md) |
| Seguridad y riesgos abiertos | [Seguridad](../governance/docs/security/README.md) |
| Decisiones de diseño | [Registro de decisiones (ADR)](../governance/docs/architecture/decision-records.md) |
| Todo el marco | [governance/readme.md](../governance/readme.md) |

---

## 14. Si vas a modificar o crear un reporte

- Reglas: [AGENTS.md](../AGENTS.md). Guía: [crear un reporte nuevo](../governance/docs/development/report-creation-guide.md) y la skill [reportes-ejecutor](../governance/skills/reportes-ejecutor/SKILL.md).
- Un reporte = un módulo `.py` con un `ReporteLote`: el T-SQL va dentro, **las fechas solo por tokens** (`@@F@@`, `@@F_ISO@@`, `@@F_ANT@@`…, nunca literales), registrado en `registro.py` y con **todas sus tablas** en `tablas.py`.
- Conexiones solo vía `src/reportes/db.py`, indicando servidor y base.
- Antes de cada commit:

```bat
python ..\governance\scripts\verificar.py     :: gobernanza + inventarios + pruebas
```
  Si cambias reportes, tablas o conexiones, regenera los inventarios: `python ..\governance\scripts\generar_inventario.py`. **No regeneres la línea base para destrabar** una compuerta ([ADR-0003](../governance/docs/architecture/adr/ADR-0003-linea-base-de-gobernanza.md)).

## Columnas que controlan la fecha de corte

`python main.py columnas-fecha [reporte] [--csv archivo.csv]` lista, por tabla, la columna de fecha que valida el cierre y la condición que aplica cada reporte (para indicar a Producción qué columna cargar). Doc: `governance/docs/data/columnas-fecha-de-corte.md`.
