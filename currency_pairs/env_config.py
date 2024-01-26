"""Util functions module."""
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

__all__ = (
    "get_config_path",
    "maybe_load_env",
)


def get_config_path() -> Path:
    prefix = os.getenv("PATH_PREFIX", "services/utils")
    config = os.getenv("SERVICE_CONFIG_PATH", "config/config.yml")
    return Path(prefix) / Path(config)


def maybe_load_env() -> None:
    """Load .env if needed."""
    if os.getenv("APP_ENVIRONMENT", None) is None:
        load_dotenv()
