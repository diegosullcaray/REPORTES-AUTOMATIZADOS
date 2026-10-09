# Clasificación

| Clase | Ejemplos | Tratamiento |
|---|---|---|
| **Restringido** | credenciales, `.env`, documentos de identidad de clientes (`TIPO_DOC`/`NUM_DOC`) | nunca al repositorio; salidas fuera de git; envío solo a destinatarios autorizados |
| **Confidencial** | saldos por cliente, castigos, provisiones, cartera | `data/outputs/` ignorado por git; no pegar en chats externos |
| **Interno** | agregados por territorio/producto | correo interno |
