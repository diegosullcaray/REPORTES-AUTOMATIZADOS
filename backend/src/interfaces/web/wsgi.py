"""Punto de entrada WSGI de la API: conecta los adaptadores, crea la aplicación de Django y arranca la cola de ejecuciones."""

from __future__ import annotations

import os

import composicion  # noqa: F401 - conecta los adaptadores reales a los puertos y carga el .env

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "interfaces.web.settings")

from django.core.wsgi import get_wsgi_application  # noqa: E402

from aplicacion.puertos import puertos  # noqa: E402

application = get_wsgi_application()
puertos().cola.iniciar()   # marca como interrumpidas las que quedaron a medias y arranca el trabajador (una sola vez por proceso)
