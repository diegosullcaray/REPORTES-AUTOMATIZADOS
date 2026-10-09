# Scripts de gobernanza

| Script | Para qué |
|---|---|
| [`verificar.py`](./verificar.py) | Un solo comando antes de cada commit: gobernanza + inventario + pruebas (segundos, sin conectarse a BD) |
| [`validar_gobernanza.py`](./validar_gobernanza.py) | Motor de reglas (`--listar` muestra el catálogo y su porqué) con línea base ([ADR-0003](../docs/architecture/adr/ADR-0003-linea-base-de-gobernanza.md)) |
| [`generar_inventario.py`](./generar_inventario.py) | Deriva del código el [inventario de módulos](../docs/architecture/module-inventory.md); `--check` falla si quedó viejo |

```bash
python governance/scripts/verificar.py
python governance/scripts/validar_gobernanza.py --listar
python governance/scripts/validar_gobernanza.py --sin-linea-base      # pasivo completo
python governance/scripts/validar_gobernanza.py --guardar-linea-base  # SOLO al reducir deuda
```
