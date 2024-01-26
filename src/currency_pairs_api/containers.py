"""Container of application.

Contains packages with components, config and higher level services.
"""
# pylint: disable=[no-member, unsubscriptable-object]
import logging

from dependency_injector import containers, providers

from src.currency_pairs_api.env_config import get_config_path, maybe_load_env
from src.currency_pairs_api.services.reverse_url import ReverseUrlService

__all__ = ("create_container",)

logger = logging.getLogger(__name__)


class Container(containers.DeclarativeContainer):
    """Container with components, config and services."""

    config = providers.Configuration()

    reverse_url: providers.Singleton[ReverseUrlService] = providers.Singleton(
        ReverseUrlService,
    )


def create_container() -> Container:
    maybe_load_env()
    config_path = get_config_path()
    container = Container()
    container.config.from_yaml(config_path)

    container.wire(packages=["src.currency_pairs_api"])
    return container
