"""Configuration loader for Conscious.

Reads ~/.conscious/config.yaml with fallback to config/default.yaml.
"""

import importlib.resources
import os
from pathlib import Path
from typing import Any

import yaml


# Repo-relative path (works in dev checkout)
_REPO_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "default.yaml"
# Bundled fallback (works after pip install)
_PACKAGE_CONFIG_DIR = "conscious.data"
_PACKAGE_CONFIG_FILE = "default.yaml"
# User override
USER_CONFIG_PATH = Path(os.path.expanduser("~/.conscious/config.yaml"))


def _get_default_config_path() -> Path | None:
    """Resolve the default config path, checking repo then package data."""
    if _REPO_CONFIG_PATH.exists():
        return _REPO_CONFIG_PATH

    # Try package data (bundled via pyproject.toml package-data)
    try:
        ref = importlib.resources.files(_PACKAGE_CONFIG_DIR) / _PACKAGE_CONFIG_FILE
        with importlib.resources.as_file(ref) as p:
            if p.exists():
                return p
    except (ModuleNotFoundError, FileNotFoundError, TypeError):
        pass

    return None


def load_config(config_path: Path | str | None = None) -> dict[str, Any]:
    """Load configuration from YAML file.

    Priority:
        1. Explicit config_path argument
        2. ~/.conscious/config.yaml (user config)
        3. config/default.yaml (bundled default)

    Returns:
        Merged configuration dictionary.
    """
    if config_path is not None:
        path = Path(config_path).expanduser()
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {path}")
        return _load_yaml(path)

    # Load default first, then overlay user config
    config = {}
    default_path = _get_default_config_path()
    if default_path is not None:
        config = _load_yaml(default_path)

    if USER_CONFIG_PATH.exists():
        user_config = _load_yaml(USER_CONFIG_PATH)
        config = _deep_merge(config, user_config)

    if not config:
        raise FileNotFoundError(
            f"No configuration found. Expected one of:\n"
            f"  - {USER_CONFIG_PATH}\n"
            f"  - {_REPO_CONFIG_PATH}"
        )

    return config


def get_config_value(config: dict[str, Any], key_path: str, default: Any = None) -> Any:
    """Get a nested config value using dot notation.

    Example:
        get_config_value(config, "moshi.device", "cpu")
    """
    keys = key_path.split(".")
    current = config
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load a YAML file and return its contents as a dict."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return data if isinstance(data, dict) else {}


def _deep_merge(base: dict, override: dict) -> dict:
    """Deep merge two dictionaries. Override values take precedence."""
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result
