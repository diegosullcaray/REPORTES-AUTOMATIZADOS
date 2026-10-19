"""Ajustes de Django para la API de la web: sin base de datos, sin sesiones de Django (la sesión es nuestra cookie firmada) y sin plantillas.

Solo escucha en local (la web de Next.js la consume por proxy en /api). La fuente de verdad de las credenciales es el .env.
"""

from __future__ import annotations

import os
import secrets

# La sesión de la web firma su propia cookie (modulos/sistema/aplicacion/casos_uso/sesion.py); esta clave solo satisface a Django.
SECRET_KEY = os.environ.get("SESION_SECRETO") or secrets.token_urlsafe(50)
DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost", "testserver"]

INSTALLED_APPS = [
    "modulos.sistema.interfaces.web",
    "modulos.reportes.interfaces.web",
    "modulos.notificaciones.interfaces.web",
    "modulos.integraciones.interfaces.web",
    "modulos.diccionario.interfaces.web",
]

MIDDLEWARE = [
    "config.middleware.sesion_obligatoria",
    "config.middleware.TraducirErrores",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
DATABASES: dict = {}          # los datos están en SQL Server y los lee la infraestructura, no el ORM
APPEND_SLASH = False          # las URL de la API no llevan barra final
USE_TZ = False
DEFAULT_CHARSET = "utf-8"
LANGUAGE_CODE = "es"
TIME_ZONE = "America/Lima"
