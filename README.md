# REPORTES-AUTOMATIZADOS

Automatización en Python de los reportes de Financiera Confianza sobre 3 bases de datos (`dw_raw`, `rcc`, `slc`).

- Gobierno, estructura, catálogo y reglas: **[GOBIERNO.md](GOBIERNO.md)**
- Procedimientos manuales heredados: [docs/procedimientos](docs/procedimientos/procedimientos_manuales_legado.md)

```
pip install -r requirements.txt
cp .env.example .env      # completar credenciales
python main.py listar
python main.py probar-conexiones
```
