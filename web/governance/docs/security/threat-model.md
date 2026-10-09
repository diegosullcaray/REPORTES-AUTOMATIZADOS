# Modelo de amenazas

| Activo | Amenaza | Control |
|---|---|---|
| Cuenta de correo MIS y webhook de Google Chat | filtración por macros/documentos; envío masivo no deseado | solo `.env`; prueba a un correo antes de enviar a la lista; `--conforme` obligatorio; no reenviar sin `--reenviar` |
| Credenciales de BD | filtración vía repositorio | solo `.env`; regla `secretos-en-codigo` |
| Servidor `rcc` / base `DW_Raw_v2` (escritura; hoy con usuario `master`) | ejecución accidental o dos veces | usuario dedicado de mínimo privilegio; abortos por validación |
| Datos de clientes en `data/outputs/` | fuga por git o correo | `data/outputs/*` ignorado; clasificación [restringido/confidencial](../data/classification.md) |
| SQL dinámico (`PROV_PROY_<fecha>`) | inyección | la fecha se genera con `strftime` de una `date`, no de texto libre |
