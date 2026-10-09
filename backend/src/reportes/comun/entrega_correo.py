"""Entrega por correo del resumen diario (legado: macro `ActualizarSQL_AmbasHojas` de «Cartera-Sin asignar-base.xlsm»).

Flujo en dos pasos, con tu aprobación en medio:
1. `python main.py cartera-sin-asignar`            valida tablas, ejecuta, genera el Excel y la imagen del resumen y envía
                                                    una PRUEBA solo a CORREO_PRUEBA (por defecto diego.sullcaray@confianza.pe).
2. `python main.py cartera-sin-asignar --correo todos --conforme`
                                                    cuando estés conforme con la prueba, envía ese mismo correo a toda la lista
                                                    (con la cuenta MIS) y avisa al webhook de Google Chat.

El paso 2 no consulta de nuevo: reutiliza el Excel y la imagen de la prueba aprobada (guardados en un archivo de estado) y
se niega a enviar si no hubo prueba, si falta `--conforme` o si ya se envió a todos (salvo `--reenviar`).
Credenciales y destinatarios: `.env` y `data/inputs/correos_cartera_sin_asignar.txt`; nada va en el código.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd

from ..registro import carpeta_salida
from . import correo
from ..config import ConfiguracionError
from .imagen import render_resumen_jpg

SALIDA_OK, SALIDA_ERROR, SALIDA_CONFIG = 0, 1, 2
FIRMA = ("Sistemas de Información de Gestión", "Las Begonias 441, Ofi. 238C, San Isidro", "Edificio Plaza del Sol - San Isidro", "Lima - Perú")


def html_correo(fecha: str, con_logo: bool, prueba: bool) -> str:
    aviso = ("<p style='background:#fff3cd;padding:8px;border:1px solid #e0c36a'><b>CORREO DE PRUEBA</b>: aún no se envió a los "
             "destinatarios. Si estás conforme, indica que se envíe.</p>") if prueba else ""
    logo = "<img src='cid:Logo_Confianza.jpg' width='180'>" if con_logo else ""
    return (
        "<html><body style='font-family: Arial, sans-serif; font-size: 13px; color: #333;'>" + aviso +
        "Buenos días,<br><br>"
        f"Adjunto la tabla resumen y el archivo correspondiente a los datos del <b>{fecha}</b>:<br><br>"
        "<img src='cid:Reporte_Temporal.jpg'><br><br>"
        "Saludos cordiales,<br><br>"
        "<table border='0' cellspacing='0' cellpadding='0'><tr>"
        f"<td style='padding-right:15px; vertical-align:middle;'>{logo}</td>"
        "<td style='border-left: 2px solid #005696; padding-left: 15px; vertical-align: top; font-size: 12px; color: #005696;'>"
        f"<b style='font-size: 13px; color: #0081c6;'>{FIRMA[0]}</b><br>{FIRMA[1]}<br>{FIRMA[2]}<br>{FIRMA[3]}<br>"
        "<a href='https://www.confianza.pe' style='font-weight:bold; color:#003366;'>www.confianza.pe</a>"
        "</td></tr></table></body></html>"
    )


class EntregaCorreoResumen:
    """Hook de `ReporteLote.entrega`: genera la imagen del resumen y envía el correo (prueba o todos)."""

    def __init__(self, asunto: str = "Reporte Sin Asignar - {fecha}") -> None:
        self.asunto = asunto

    # --- CLI
    def argumentos(self, parser) -> None:
        parser.add_argument("--correo", choices=("no", "prueba", "todos"), default="prueba",
                            help="no: solo Excel · prueba (defecto): envía solo a CORREO_PRUEBA · todos: envía a toda la lista (exige --conforme)")
        parser.add_argument("--conforme", action="store_true", help="confirmo que revisé la prueba; requerido con --correo todos")
        parser.add_argument("--reenviar", action="store_true", help="permite enviar a todos otra vez el mismo día")

    # --- estado de la prueba aprobada
    @staticmethod
    def _ruta_estado(cortes) -> Path:
        return carpeta_salida("cartera-sin-asignar") / f"estado_envio_{cortes.corte:%Y%m%d}.json"

    def _leer_estado(self, cortes) -> dict:
        ruta = self._ruta_estado(cortes)
        return json.loads(ruta.read_text(encoding="utf-8")) if ruta.exists() else {}

    def _guardar_estado(self, cortes, estado: dict) -> None:
        ruta = self._ruta_estado(cortes)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        ruta.write_text(json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8")

    # --- envío
    def _enviar(self, cortes, excel: Path, imagen: Path, *, prueba: bool) -> list[str]:
        cfg = correo.config_desde_env()
        destinatarios = [cfg.correo_prueba] if prueba else correo.leer_destinatarios()
        fecha = f"{cortes.corte:%Y-%m-%d}"
        con_logo = bool(cfg.logo and cfg.logo.exists())
        en_linea = {"Reporte_Temporal.jpg": imagen}
        if con_logo:
            en_linea["Logo_Confianza.jpg"] = cfg.logo
        asunto = ("[PRUEBA] " if prueba else "") + self.asunto.format(fecha=fecha)
        msg = correo.construir_mensaje(cfg, asunto, html_correo(fecha, con_logo, prueba), destinatarios, en_linea=en_linea, adjuntos=[excel])
        correo.enviar(cfg, msg, destinatarios)
        return destinatarios

    def antes(self, a, cortes) -> int | None:
        """`--correo todos`: envía a todos lo ya validado en la prueba, sin consultar de nuevo."""
        if a.correo != "todos":
            return None
        try:
            if not a.conforme:
                print("✗ Para enviar a todos debes confirmar con --conforme, después de revisar el correo de prueba.")
                return SALIDA_CONFIG
            estado = self._leer_estado(cortes)
            if not estado.get("prueba"):
                print(f"✗ No hay una prueba enviada para {cortes.corte:%Y-%m-%d}. Primero ejecuta `python main.py cartera-sin-asignar` "
                      "(envía solo a tu correo de prueba), revísala y luego repite con --correo todos --conforme.")
                return SALIDA_CONFIG
            if estado.get("todos") and not a.reenviar:
                print(f"✗ Ya se envió a todos el {estado['todos']}. Usa --reenviar si de verdad quieres enviarlo otra vez.")
                return SALIDA_CONFIG
            excel, imagen = Path(estado["excel"]), Path(estado["imagen"])
            if not excel.exists() or not imagen.exists():
                print("✗ Faltan el Excel o la imagen de la prueba aprobada; vuelve a ejecutar la prueba.")
                return SALIDA_CONFIG
            destinatarios = self._enviar(cortes, excel, imagen, prueba=False)
            ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            estado["todos"] = ahora
            self._guardar_estado(cortes, estado)
            print(f"✓ Correo enviado a {len(destinatarios)} destinatarios con la cuenta MIS: {excel.name}")
            self._avisar_chat(cortes, excel, destinatarios, ahora)
            return SALIDA_OK
        except ConfiguracionError as exc:
            print(f"✗ Configuración: {exc}")
            return SALIDA_CONFIG
        except correo.CorreoError as exc:
            print(f"✗ {exc}")
            return SALIDA_ERROR

    def despues(self, a, lote, resultados: list[pd.DataFrame], cortes, ruta_excel: Path) -> int:
        """Tras validar y exportar: imagen del resumen + correo de PRUEBA (o nada con `--correo no`)."""
        if a.correo == "no":
            return SALIDA_OK
        try:
            resumen = lote.resumenes[0]
            imagen = render_resumen_jpg(resultados[resumen.origen], resumen, ruta_excel.parent / f"Reporte_Temporal_{cortes.corte:%Y-%m-%d}.jpg")
            print(f"✓ Imagen del resumen: {imagen}")
            if a.correo == "todos":  # `--correo todos` sin prueba previa llega aquí solo si antes() no lo atajó
                print("✗ El envío a todos se hace con la prueba ya aprobada: ejecuta primero sin --correo todos.")
                return SALIDA_CONFIG
            destinatarios = self._enviar(cortes, ruta_excel, imagen, prueba=True)
            estado = {"prueba": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "excel": str(ruta_excel), "imagen": str(imagen), "todos": None}
            self._guardar_estado(cortes, estado)
            print(f"✓ Correo de PRUEBA enviado a {destinatarios[0]}. Revísalo; cuando estés conforme:\n"
                  f"    python main.py cartera-sin-asignar --fecha-corte {cortes.corte:%Y-%m-%d} --correo todos --conforme")
            return SALIDA_OK
        except ConfiguracionError as exc:
            print(f"✗ El Excel se generó, pero no se envió el correo: {exc}")
            return SALIDA_CONFIG
        except correo.CorreoError as exc:
            print(f"✗ El Excel se generó, pero {exc}")
            return SALIDA_ERROR

    def _avisar_chat(self, cortes, excel: Path, destinatarios: list[str], ahora: str) -> None:
        url = correo.config_desde_env().webhook
        if not url:
            print("AVISO: sin GOOGLE_CHAT_WEBHOOK_URL en el .env; no se avisó a Google Chat.")
            return
        texto = ("*REPORTE GENERADO Y ENVIADO EXITOSAMENTE*\n\n"
                 f"• *Fecha consulta:* {cortes.corte:%Y-%m-%d}\n• *Archivo adjunto:* {excel.name}\n"
                 f"• *Destinatarios:* {'; '.join(destinatarios)}\n• *Hora de ejecución:* {ahora}")
        try:
            correo.notificar_chat(url, texto)
            print("✓ Aviso enviado a Google Chat.")
        except correo.CorreoError as exc:
            print(f"AVISO: {exc}")
