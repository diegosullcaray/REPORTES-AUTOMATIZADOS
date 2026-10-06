# Hallazgos

| ID | Severidad | Hallazgo | Estado |
|---|---|---|---|
| SEC-001 | **Crítica** | Contraseñas en texto plano en el legado: usuario `master` (escritura) en el script de CMG Mora, y un usuario SQL de lectura en los scripts de Bancarizados y Extranjeros. Siguen en `docs/LEGADO/` y en el historial de git | Abierto |
| SEC-002 | Alta | `cmg_mora` usa una cuenta con privilegios amplios para operaciones puntuales | Abierto |
| SEC-003 | Media | Cachés `.pkl` y TXT de salida con datos reales dentro de `docs/LEGADO/` (versionados) | Abierto |

Los valores no se reproducen en esta documentación.
