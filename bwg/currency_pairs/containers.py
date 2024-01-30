"""Container of application.

Contains packages with components, config and higher level services.
"""
# pylint: disable=[no-member, unsubscriptable-object]
import logging

from dependency_injector import containers, providers

from bwg.currency_pairs.services.processor import ProcessorService
from bwg.currency_pairs.services.coingecko import CoinGeckoService
from bwg.lib.env_config import get_config_path, maybe_load_env
from bwg.lib.postgres.containers import PostgresContainer
from bwg.lib.repositories.currency_pairs import CurrencyPairsRepository
from bwg.currency_pairs.services.binance_service import BinanceService

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

    binance:  providers.Singleton[BinanceService] = providers.Singleton(
        BinanceService,
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
        binance=binance,
    )


def create_container() -> Container:
    maybe_load_env()
    config_path = get_config_path()
    container = Container()
    container.config.from_yaml(config_path)

    container.wire(packages=["bwg.currency_pairs"])
    return container
