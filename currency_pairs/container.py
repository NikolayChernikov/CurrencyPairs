"""Container of application.

Contains packages with components, config and higher level services.
"""
import logging

from dependency_injector import containers
from currency_pairs.env_config import get_config_path, maybe_load_env

__all__ = ("create_container",)

logger = logging.getLogger(__name__)


class Container(containers.DeclarativeContainer):
    ...


def create_container() -> Container:
    maybe_load_env()
    config_path = get_config_path()
    container = Container()
    container.config.from_yaml(config_path)

    container.wire(packages=["currency_pairs"])
    return container
