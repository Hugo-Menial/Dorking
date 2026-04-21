"""Gestion de la configuration — clés API chiffrées via keyring OS."""

import json
import os
from dataclasses import dataclass, field

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "config.json")
KEYRING_SERVICE = "dorking_tool"

# Champs sensibles stockés dans le keyring OS, pas dans le JSON
API_KEY_FIELDS = [
    "google_api_key",
    "google_cse_id",
    "bing_api_key",
    "shodan_api_key",
    "anthropic_api_key",
]


def _keyring_available() -> bool:
    try:
        import keyring
        keyring.get_password(KEYRING_SERVICE, "__probe__")
        return True
    except Exception:
        return False


def _save_secret(key: str, value: str):
    try:
        import keyring
        if value:
            keyring.set_password(KEYRING_SERVICE, key, value)
        else:
            try:
                keyring.delete_password(KEYRING_SERVICE, key)
            except Exception:
                pass
    except Exception:
        pass


def _load_secret(key: str) -> str:
    try:
        import keyring
        return keyring.get_password(KEYRING_SERVICE, key) or ""
    except Exception:
        return ""


@dataclass
class AppConfig:
    google_api_key: str = ""
    google_cse_id: str = ""
    bing_api_key: str = ""
    shodan_api_key: str = ""
    anthropic_api_key: str = ""
    default_engines: list[str] = field(default_factory=lambda: ["DuckDuckGo"])
    default_results: int = 10
    theme: str = "dark"
    export_dir: str = os.path.expanduser("~/Desktop")
    watchdog_storage: str = os.path.join(
        os.path.dirname(__file__), "..", "data", "watchdog_jobs.json"
    )
    # True si les clés sont stockées dans le keyring OS
    keyring_enabled: bool = False


def load_config() -> AppConfig:
    path = os.path.abspath(CONFIG_PATH)
    cfg = AppConfig()

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in data.items():
            # Les champs API ne sont pas dans le JSON si keyring est actif
            if k not in API_KEY_FIELDS and hasattr(cfg, k):
                setattr(cfg, k, v)
        cfg.keyring_enabled = data.get("keyring_enabled", False)

    if cfg.keyring_enabled and _keyring_available():
        for field_name in API_KEY_FIELDS:
            value = _load_secret(field_name)
            if value:
                setattr(cfg, field_name, value)
    else:
        # Fallback : lecture depuis le JSON (migration depuis ancienne config)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for field_name in API_KEY_FIELDS:
                if field_name in data:
                    setattr(cfg, field_name, data[field_name])

    return cfg


def save_config(cfg: AppConfig):
    path = os.path.abspath(CONFIG_PATH)
    os.makedirs(os.path.dirname(path), exist_ok=True)

    use_keyring = _keyring_available()
    cfg.keyring_enabled = use_keyring

    if use_keyring:
        for field_name in API_KEY_FIELDS:
            _save_secret(field_name, getattr(cfg, field_name, ""))

    # JSON : config non-sensible uniquement
    json_data = {
        "default_engines": cfg.default_engines,
        "default_results": cfg.default_results,
        "theme": cfg.theme,
        "export_dir": cfg.export_dir,
        "watchdog_storage": cfg.watchdog_storage,
        "keyring_enabled": use_keyring,
    }

    if not use_keyring:
        # Keyring indisponible : fallback JSON (avertissement dans les logs)
        import warnings
        warnings.warn(
            "keyring indisponible — clés API stockées en JSON. "
            "Installez 'keyring' pour un stockage sécurisé.",
            UserWarning, stacklevel=2
        )
        for field_name in API_KEY_FIELDS:
            json_data[field_name] = getattr(cfg, field_name, "")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)


def keyring_status() -> dict:
    """Retourne le statut du keyring pour affichage dans les paramètres."""
    available = _keyring_available()
    backend = ""
    if available:
        try:
            import keyring
            backend = type(keyring.get_keyring()).__name__
        except Exception:
            backend = "inconnu"
    return {
        "available": available,
        "backend": backend,
        "message": (
            f"Keyring actif ({backend}) — clés chiffrées par le système"
            if available
            else "Keyring indisponible — installez 'keyring' (pip install keyring)"
        ),
    }
