"""Entrega de archivos generados por Google Chat (mensaje directo con adjunto), con la cuenta de Google autorizada en la web.

Destinatarios por reporte en el .env: `ENTREGA_CHAT_<REPORTE>` (p. ej. ENTREGA_CHAT_CMG_MORA), correos separados por coma.
Se edita desde la web (pestaña General del reporte). Nada de direcciones en el código.
"""

from __future__ import annotations

import os
from pathlib import Path

from dominio.entregas import correos_validos, variable_chat


def destinatarios(reporte: str) -> list[str]:
    return correos_validos(os.getenv(variable_chat(reporte), ""))


def enviar(reporte: str, archivos: list[Path], texto: str) -> bool:
    """Envía `archivos` a cada destinatario. True si llegó a todos; imprime el resultado para el log."""
    from infraestructura.google import cliente as g   # import diferido: solo hace falta si se pide la entrega

    para = destinatarios(reporte)
    if not para:
        print(f"✗ No hay a quién enviar por Google Chat: falta {variable_chat(reporte)} en el .env (se edita en la pestaña General del reporte).")
        return False
    faltan = [a.name for a in archivos if not a.exists()]
    if faltan:
        print(f"✗ No se encontró el archivo a enviar: {', '.join(faltan)}")
        return False
    try:
        token = g.token_de_acceso()
    except g.GoogleError as exc:
        print(f"✗ No se pudo enviar por Google Chat: {exc}")
        return False
    ok = True
    for correo in para:
        try:
            g.enviar_chat(token, correo, texto, archivos)
            print(f"✓ Enviado por Google Chat a {correo}: {', '.join(a.name for a in archivos)}")
        except g.GoogleError as exc:
            print(f"✗ No se pudo enviar por Google Chat a {correo}: {exc}")
            ok = False
    return ok
