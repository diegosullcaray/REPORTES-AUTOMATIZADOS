# Modelo de amenazas

| Activo | Amenaza | Control |
|---|---|---|
| Credenciales de BD | filtración vía repositorio | solo `.env`; regla `secretos-en-codigo` |
| BD `dw_raw` (escritura) | ejecución accidental o dos veces | usuario dedicado de mínimo privilegio; abortos por validación |
| Datos de clientes en `salidas/` | fuga por git o correo | `salidas/*` ignorado; clasificación [restringido/confidencial](../data/classification.md) |
| SQL dinámico (`PROV_PROY_<fecha>`) | inyección | la fecha se genera con `strftime` de una `date`, no de texto libre |
