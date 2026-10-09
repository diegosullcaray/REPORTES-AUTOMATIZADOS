# Catálogo de reportes

Numeración y responsable = carpetas del legado (`docs/LEGADO`): **Diarias** 02, 04; **Piero** 01–09; **Erick** 01–03 (ver [registro](../../../backend/src/reportes/registro.py) y `python main.py listar`).

Todos son ejecutables con `python main.py <comando> --fecha-corte AAAA-MM-DD`. Qué hace cada comando, sus tablas críticas y su salida: [catálogo de comandos](../development/runbooks/comandos.md) (generado). Quién pide cada reporte y a quién se entrega (según las notas heredadas):

| Comando | Solicitante / destinatarios | Nota clave |
|---|---|---|
| `cmg-mora` | MIS / Riesgos | diario; lunes toma el sábado; aborta si provisiones = 0 |
| `cartera-sin-asignar` | MIS | diario; Excel base en `data/inputs/cartera_sin_asignar_base.xlsm` |
| `desembolsos-por-canal` | Sergio, Sebastián; cc Abigail, Michel | canales CT/BT; si no hay acceso a producción, pedir que lo ejecuten |
| `fondeo-estable` | Eddy Martínez; cc Michael, Abigail | inicio de mes (día ~3); tabla tipo WAS |
| `heredados-pdm` | Carla Campo, Ricardo Lazo, Álvaro Calderón; cc Michael | validar Cubo y tablas PDM completos |
| `contratacion-electronica`, `clientes-rurales-migrantes` | Manuel Siccha, Michel | correo con n.º de operaciones y monto; rurales: 3 últimos cierres |
| `giovanni-captaciones`, `giovanni-seguros`, `giovanni-cartera-agro` | Giovanni | seguros: ceros ⇒ «sin asignar»; cartera agro con dos cortes |
| `saca-tu-garra` | Giancarlos | entregar 8:00–8:30 AM |
| `saldo-medio-vigente` | Diana García | saldo medio = suma de saldos diarios ÷ días del mes |
| `tapp-saldo-medio-territorio` | Edy | **escribe** `appj.dbo.salmediovigente1`; exige `--confirmar-escritura` |
| `michael-captaciones`, `michael-castigos` | Michael / Riesgos / Manuel / Giovanni | castigos puede salir vacío; captaciones no |
| `clientes-jovenes`, `productos-verdes` | Manuel Siccha | directorio |
| `bancarizados`, `bancarizados-producto`, `clientes-extranjeros`, `indicadores-clientes` | Finanzas / Directorio | lógica Python propia |

Los destinatarios y el formato del correo siguen el [procedimiento heredado](./procedimientos_manuales_legado.md). El envío por correo **no** está automatizado (ver [roadmap](./roadmap.md)).
