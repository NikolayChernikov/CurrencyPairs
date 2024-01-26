"""Util functions module."""
import os
from pathlib import Path

from dotenv import load_dotenv

__all__ = (
    "get_config_path",
    "maybe_load_env",
)


def get_config_path() -> Path:
    config = os.getenv("SERVICE_CONFIG_PATH", "config/config.yml")
    return Path(config)


def maybe_load_env() -> None:
    """Load .env if needed."""
    if os.getenv("APP_ENVIRONMENT", None) is None:
        load_dotenv()
