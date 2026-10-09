# Hallazgos

| ID | Severidad | Hallazgo | Estado |
|---|---|---|---|
| SEC-001 | **Crítica** | Contraseñas en texto plano en el legado: usuario `master` (escritura) en el script de CMG Mora, y un usuario SQL de lectura en los scripts de Bancarizados y Extranjeros. Siguen en `docs/LEGADO/` y en el historial de git | Abierto |
| SEC-002 | Alta | `cmg_mora` usa una cuenta con privilegios amplios para operaciones puntuales | Abierto |
| SEC-003 | Media | Cachés `.pkl` y TXT de salida con datos reales dentro de `docs/LEGADO/` (versionados) | Abierto |
| SEC-004 | **Crítica** | `governance/tasks/tareasdiarias.md` (subido al remoto) traía en texto plano la contraseña de aplicación de la cuenta de correo `mis@confianza.pe` y la clave+token del webhook de Google Chat (copiados de la macro del legado). Ya están en el historial de git; es probable que también estén dentro del VBA de `Cartera-Sin asignar-base.xlsm` | Abierto (valores ocultos en el archivo; **rotar** la contraseña de aplicación y regenerar el webhook) |

Los valores no se reproducen en esta documentación.
