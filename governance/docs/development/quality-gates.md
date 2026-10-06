# Compuertas de calidad

`python governance/scripts/verificar.py` ejecuta, en orden:

| Fase | Bloquea cuando | Corrección |
|---|---|---|
| Gobernanza | hay un **hallazgo nuevo** fuera de la línea base (o cualquier error) | corregirlo; no regenerar la línea base ([ADR-0003](../architecture/adr/ADR-0003-linea-base-de-gobernanza.md)) |
| Inventario | `module-inventory.md` quedó viejo | `python governance/scripts/generar_inventario.py` |
| Pruebas | falla pytest | arreglar la causa raíz |

## Reglas (`validar_gobernanza.py --listar`)
Errores: `secretos-en-codigo`, `conexion-solo-en-db`, `rutas-absolutas`, `registro-sincronizado` (módulos inexistentes/sin `main`/base inválida), `env-example-completo`, `gitignore-protege-datos`.
Errores adicionales: `tabla-sin-registrar` (tabla usada por el código/SQL sin registrar en `tablas.py`, o reporte sin tablas).
Avisos: `tabla-fecha-por-validar` (columna de fecha inferida por prefijo; validar con el DBA), `nombres-canonicos`, `prueba-vecina`, `sql-sin-reporte` (deuda visible, congelada en la línea base).
