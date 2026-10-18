"""Proveedores de IA con API key (OpenAI, Anthropic, Gemini, Mistral, OpenRouter, Ollama o cualquier endpoint compatible con OpenAI).

El proveedor se deduce de la URL de la API, como en Dokploy; aquí solo se listan sus modelos (verifica la URL y la clave). Biblioteca estándar.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

from core.excepciones import ErrorIntegracion

# Proveedores sin endpoint de modelos: lista fija.
FIJOS = {
    "perplexity": ["sonar-deep-research", "sonar-reasoning-pro", "sonar-reasoning", "sonar-pro", "sonar"],
    "zai": ["glm-5", "glm-4.7"],
    "minimax": ["MiniMax-M2.7"],
}
_POR_URL = (
    ("api.openai.com", "openai"), ("azure.com", "azure"), ("api.anthropic.com", "anthropic"), ("api.cohere.ai", "cohere"),
    ("api.perplexity.ai", "perplexity"), ("api.mistral.ai", "mistral"), (":11434", "ollama"), ("ollama", "ollama"),
    ("api.deepinfra.com", "deepinfra"), ("generativelanguage.googleapis.com", "gemini"), ("openrouter.ai", "openrouter"),
    ("api.z.ai", "zai"), ("api.minimax.io", "minimax"),
)


def proveedor_de(api_url: str) -> str:
    return next((nombre for marca, nombre in _POR_URL if marca in api_url), "custom")


def _ids(respuesta) -> list[str]:
    """Los distintos proveedores devuelven la lista como [..], {models: [..]}, {data: [..]} o bajo otra clave."""
    if isinstance(respuesta, dict):
        respuesta = respuesta.get("models") or respuesta.get("data") or next((v for v in respuesta.values() if isinstance(v, list)), [])
    return sorted({m.get("id") or m.get("name") for m in respuesta if isinstance(m, dict) and (m.get("id") or m.get("name"))})


def modelos(api_url: str, api_key: str) -> list[str]:
    """Modelos disponibles con esa clave. Lanza ErrorIntegracion si la URL o la clave no sirven."""
    base = api_url.rstrip("/")
    proveedor = proveedor_de(base)
    if proveedor in FIJOS:
        return FIJOS[proveedor]
    cabeceras = {"Accept": "application/json"}
    if proveedor == "anthropic":
        cabeceras |= {"x-api-key": api_key, "anthropic-version": "2023-06-01"}
        url = f"{base}/models"
    elif proveedor == "gemini":
        url = f"{base}/models?key={urllib.parse.quote(api_key)}"
    elif proveedor == "ollama":
        url = f"{base}/api/tags"
        if api_key:
            cabeceras["Authorization"] = f"Bearer {api_key}"
    else:
        if not api_key:
            raise ErrorIntegracion("Falta la API key.")
        cabeceras["Authorization"] = f"Bearer {api_key}"
        url = f"{base}/models"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=cabeceras), timeout=20) as resp:  # noqa: S310 - la URL la configura quien administra el sistema
            return _ids(json.loads(resp.read().decode("utf-8")))
    except urllib.error.HTTPError as exc:
        raise ErrorIntegracion(f"El proveedor respondió {exc.code}: revisa la API key y la URL.") from exc
    except (urllib.error.URLError, OSError, ValueError) as exc:
        raise ErrorIntegracion(f"No se pudo conectar con {base} ({type(exc).__name__}).") from exc
