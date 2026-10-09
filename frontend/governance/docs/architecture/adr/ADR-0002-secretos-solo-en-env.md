# ADR-0002: Secretos solo en `.env`

- Estado: Vigente · Fecha: 2026-10-06

## Contexto
El legado incluía contraseñas en texto plano en scripts versionados ([hallazgo](../../security/findings.md)).

## Decisión
Credenciales únicamente en `.env` (ignorado por git), documentado en `.env.example`. La regla `secretos-en-codigo` bloquea literales; `verificar.py` la ejecuta.

## Consecuencias
Las credenciales ya expuestas deben rotarse: borrar el literal no las revoca.
