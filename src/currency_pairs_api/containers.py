"""Container of application.

Contains packages with components, config and higher level services.
"""
# pylint: disable=[no-member, unsubscriptable-object]
import logging

from dependency_injector import containers, providers

from src.currency_pairs_api.services.currency_pairs import CurrencyPairsService
from src.currency_pairs_api.services.reverse_url import ReverseUrlService
from src.lib.env_config import get_config_path, maybe_load_env
from src.lib.repositories.currency_pairs import CurrencyPairsRepository
from src.lib.monitoring.containers import MonitoringContainer
from src.lib.postgres.containers import PostgresContainer

__all__ = ("create_container",)

logger = logging.getLogger(__name__)


class Container(containers.DeclarativeContainer):
    """Container with components, config and services."""

    config = providers.Configuration()

    postgres_package: providers.Container[PostgresContainer] = providers.Container(
        PostgresContainer,
        config=config.postgres,
    )

    reverse_url: providers.Singleton[ReverseUrlService] = providers.Singleton(
        ReverseUrlService,
    )

    currency_pairs: providers.Singleton[CurrencyPairsService] = providers.Singleton(
        CurrencyPairsService,
    )

    currency_pairs_repository: providers.Singleton[CurrencyPairsRepository] = providers.Singleton(
        CurrencyPairsRepository,
    )

    monitoring_container: providers.Container[MonitoringContainer] = providers.Container(
        MonitoringContainer,
        config=config.monitoring,
    )

    currency_pairs.add_attributes(
        db_postgres=postgres_package.db,
        currency_pairs_repository=currency_pairs_repository,
    )


def create_container() -> Container:
    maybe_load_env()
    config_path = get_config_path()
    container = Container()
    container.config.from_yaml(config_path)

    container.wire(packages=["src.currency_pairs_api"])
    return container
