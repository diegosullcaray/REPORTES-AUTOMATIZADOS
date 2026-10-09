"""Arranca el backend (API) y el frontend (web) en local con un solo comando.

    python iniciar.py                 desarrollo: API en 127.0.0.1:8000 y web en http://localhost:3000
    python iniciar.py --prod          compila la web y la sirve (npm run build + npm start)
    python iniciar.py --sin-navegador no abre el navegador
    python iniciar.py --puerto-api 8100 --puerto-web 3100

Ctrl+C detiene los dos procesos. Solo usa la biblioteca estándar: se puede lanzar con cualquier Python 3.11+.
"""

from __future__ import annotations

import argparse
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
BACKEND, FRONTEND = RAIZ / "backend", RAIZ / "frontend"
COLORES = {"api": "\033[36m", "web": "\033[35m", "iniciar": "\033[33m"}
FIN = "\033[0m"
_salida = threading.Lock()


def decir(origen: str, texto: str) -> None:
    with _salida:
        print(f"{COLORES.get(origen, '')}[{origen}]{FIN} {texto}", flush=True)


def python_del_backend() -> str:
    """El Python del entorno virtual del backend (`backend/env`); si no existe, el que ejecuta este script."""
    for ruta in (BACKEND / "env" / "Scripts" / "python.exe", BACKEND / "env" / "bin" / "python"):
        if ruta.exists():
            return str(ruta)
    decir("iniciar", "AVISO: no existe backend/env; uso el Python actual. Créalo con: cd backend && python -m venv env && env\\Scripts\\activate && pip install -r requirements.txt")
    return sys.executable


def credenciales_web_definidas() -> bool:
    """¿Hay WEB_USUARIO y WEB_CLAVE en backend/.env? Sin ellas nadie puede iniciar sesión (no se muestran los valores)."""
    env = BACKEND / ".env"
    if not env.exists():
        return False
    definidas = set()
    for linea in env.read_text(encoding="utf-8", errors="ignore").splitlines():
        clave, _, valor = linea.partition("=")
        if valor.strip() and not clave.lstrip().startswith("#"):
            definidas.add(clave.strip())
    return {"WEB_USUARIO", "WEB_CLAVE"} <= definidas


def activar_colores_en_windows() -> None:
    """Modo de terminal virtual de la consola de Windows: sin esto se verían los códigos de color como texto."""
    import ctypes

    kernel = ctypes.windll.kernel32  # type: ignore[attr-defined]
    consola, modo = kernel.GetStdHandle(-11), ctypes.c_uint32()
    if kernel.GetConsoleMode(consola, ctypes.byref(modo)):
        kernel.SetConsoleMode(consola, modo.value | 0x0004)


def puerto_ocupado(puerto: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        return s.connect_ex(("127.0.0.1", puerto)) == 0


def reenviar(origen: str, proceso: subprocess.Popen) -> None:
    for linea in proceso.stdout:  # type: ignore[union-attr]
        decir(origen, linea.rstrip())


def lanzar(origen: str, comando: list[str], cwd: Path, extra_env: dict[str, str] | None = None) -> subprocess.Popen:
    env = {**os.environ, "PYTHONUNBUFFERED": "1", "PYTHONIOENCODING": "utf-8", "FORCE_COLOR": "0", **(extra_env or {})}
    proceso = subprocess.Popen(comando, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    threading.Thread(target=reenviar, args=(origen, proceso), daemon=True).start()
    return proceso


def detener(proceso: subprocess.Popen) -> None:
    """Cierra el proceso y sus hijos (npm lanza node aparte)."""
    if proceso.poll() is not None:
        return
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(proceso.pid), "/T", "/F"], capture_output=True)
    else:
        proceso.terminate()


def esperar(url: str, proceso: subprocess.Popen, segundos: int = 90) -> bool:
    fin = time.time() + segundos
    while time.time() < fin and proceso.poll() is None:
        try:
            urllib.request.urlopen(url, timeout=2).close()
            return True
        except urllib.error.HTTPError:
            return True  # respondió (p. ej. 401 sin sesión): está arriba
        except (urllib.error.URLError, OSError):
            time.sleep(0.5)
    return False


def asegurar_dependencias_web(npm: str) -> None:
    if (FRONTEND / "node_modules").exists():
        return
    decir("iniciar", "Instalando dependencias del frontend (npm install), solo la primera vez…")
    if subprocess.run([npm, "install"], cwd=FRONTEND).returncode != 0:
        sys.exit("npm install falló: revisa la salida de arriba.")


def main() -> int:
    ap = argparse.ArgumentParser(description="Arranca la API (backend) y la web (frontend) en local.")
    ap.add_argument("--prod", action="store_true", help="compila y sirve la web (npm run build + npm start) en vez de npm run dev")
    ap.add_argument("--sin-navegador", action="store_true", help="no abrir el navegador al terminar de arrancar")
    ap.add_argument("--puerto-api", type=int, default=8000)
    ap.add_argument("--puerto-web", type=int, default=3000)
    args = ap.parse_args()

    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]  # consolas cp1252 / salida redirigida
    if os.name == "nt":
        activar_colores_en_windows()
    npm = shutil.which("npm")
    if not npm:
        return print("No encuentro npm: instala Node 20+ (https://nodejs.org) y vuelve a abrir la terminal.") or 1
    for nombre, puerto in (("API", args.puerto_api), ("web", args.puerto_web)):
        if puerto_ocupado(puerto):
            return print(f"El puerto {puerto} ({nombre}) ya está en uso: ¿ya está corriendo? Ciérralo o usa --puerto-{'api' if nombre == 'API' else 'web'} OTRO.") or 1
    if not credenciales_web_definidas():
        decir("iniciar", "AVISO: faltan WEB_USUARIO y/o WEB_CLAVE en backend/.env; sin ellas nadie podrá iniciar sesión en la web.")

    asegurar_dependencias_web(npm)
    url_api, url_web = f"http://127.0.0.1:{args.puerto_api}", f"http://localhost:{args.puerto_web}"
    if args.prod:
        decir("iniciar", "Compilando la web (npm run build)…")
        # El destino del proxy /api queda fijado al compilar: la URL de la API tiene que estar ya en el entorno del build.
        if subprocess.run([npm, "run", "build"], cwd=FRONTEND, env={**os.environ, "REPORTES_API_URL": url_api}).returncode != 0:
            return 1
    procesos = {
        "api": lanzar("api", [python_del_backend(), "-m", "uvicorn", "api.app:app", "--app-dir", "src", "--host", "127.0.0.1", "--port", str(args.puerto_api)], BACKEND),
        "web": lanzar("web", [npm, "run", "start" if args.prod else "dev", "--", "-p", str(args.puerto_web)], FRONTEND, {"REPORTES_API_URL": url_api}),
    }
    try:
        if esperar(f"{url_api}/openapi.json", procesos["api"]) and esperar(f"{url_web}/login", procesos["web"]):
            decir("iniciar", f"Listo → web {url_web}  ·  API {url_api}  ·  Ctrl+C para detener los dos")
            if not args.sin_navegador:
                webbrowser.open(url_web)
        else:
            decir("iniciar", "Algo no arrancó (mira los mensajes de arriba).")
        while all(p.poll() is None for p in procesos.values()):
            time.sleep(0.5)
        caido = next(n for n, p in procesos.items() if p.poll() is not None)
        decir("iniciar", f"El proceso «{caido}» terminó (código {procesos[caido].returncode}); detengo el otro.")
        return 1
    except KeyboardInterrupt:
        decir("iniciar", "Deteniendo…")
        return 0
    finally:
        for p in procesos.values():
            detener(p)


if __name__ == "__main__":
    sys.exit(main())
