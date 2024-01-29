"""Container of application.

Contains packages with components, config and higher level services.
"""
# pylint: disable=[no-member, unsubscriptable-object]
import logging

from dependency_injector import containers, providers

from src.currency_pairs.services.processor import ProcessorService
from src.currency_pairs.services.coingecko import CoinGeckoService
from src.lib.env_config import get_config_path, maybe_load_env
from src.lib.postgres.containers import PostgresContainer
from src.lib.repositories.currency_pairs import CurrencyPairsRepository

__all__ = ("create_container",)

logger = logging.getLogger(__name__)


class Container(containers.DeclarativeContainer):
    """Container with components, config and services."""

    # configuration from config file
    config = providers.Configuration()

    postgres_package: providers.Container[PostgresContainer] = providers.Container(
        PostgresContainer,
        config=config.postgres,
    )

    coingecko: providers.Singleton[CoinGeckoService] = providers.Singleton(
        CoinGeckoService,
    )

    currency_pairs_repository: providers.Singleton[CurrencyPairsRepository] = providers.Singleton(
        CurrencyPairsRepository,
    )

    processor: providers.Singleton[ProcessorService] = providers.Singleton(
        ProcessorService,
    )

    processor.add_attributes(
        db_postgres=postgres_package.db,
        coingecko=coingecko,
        currency_pairs_repository=currency_pairs_repository,
    )


def create_container() -> Container:
    maybe_load_env()
    config_path = get_config_path()
    container = Container()
    container.config.from_yaml(config_path)

    container.wire(packages=["src.currency_pairs"])
    return container
