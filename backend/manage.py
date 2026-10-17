#!/usr/bin/env python
"""Utilidad de Django del backend: `python manage.py runserver 127.0.0.1:8000 --noreload` arranca la API de la web.

Sin base de datos propia de Django (las bases SQL Server son de los reportes): Django es solo la capa HTTP de `config/` y los módulos.
"""

import os
import sys
from pathlib import Path


def main() -> None:
    sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    from config import composicion  # noqa: F401 - conecta los adaptadores reales a los puertos

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
