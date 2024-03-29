"""Processor module."""
# pylint: disable=broad-exception-caught
import datetime
import logging
import time
from typing import Optional

from bwg.currency_pairs.services.binance_service import BinanceService
from bwg.currency_pairs.services.coingecko import CoinGeckoService
from bwg.lib.postgres import PostgresDatabase
from bwg.lib.repositories.currency_pairs import CurrencyPairsRepository

__all__ = ("ProcessorService",)

logger = logging.getLogger(__name__)


class ProcessorService:
    """Processor service."""

    coingecko: "CoinGeckoService"
    binance: "BinanceService"
    db_postgres: "PostgresDatabase"
    currency_pairs_repository: "CurrencyPairsRepository"

    def __init__(self) -> None:
        self.binance_pairs = {
            'BTC': ['RUB', 'USDT'],
            'ETH': ['RUB', 'USDT'],
        }

        self.coingecko_pairs = {
            'BITCOIN': ['RUB', 'USD'],
            'ETHEREUM': ['RUB', 'USD'],
        }

        self.default_exchanger = 'binance'

    def run_infinity_loop(self) -> None:
        try:
            logger.info("Run infinity loop")
            exchaner = self.default_exchanger
            while True:
                pairs = None
                with self.db_postgres.session() as session:  # type: ignore[var-annotated]
                    if exchaner == 'coingecko':
                        pairs = self.coingecko.get_currency_by_pair(self.coingecko_pairs)
                    elif exchaner == 'binance':
                        pairs = self.binance.get_currency_by_pair(self.binance_pairs)
                    if not pairs:
                        self.exchanges_selector()
                    for token in pairs.keys():
                        for currency in pairs[token].keys():
                            value = pairs[token][currency]
                            to_insert = self.make_msg(token, currency, value, exchaner)
                            self.currency_pairs_repository.insert_or_update(session, **to_insert)
                            session.commit()  # type: ignore[attr-defined]
                            logger.info(to_insert)
                time.sleep(2)
        except Exception as exc:
            logger.exception(f"Failed with {exc=}.")

    def exchanges_selector(self) -> Optional[str]:
        while True:
            if not self.coingecko.ping():
                return 'coingecko'
            if not self.binance.ping():
                return 'binance'
            logger.error("Could not connect to exchanges")
            time.sleep(60)

    @staticmethod
    def make_msg(token: str, currency: str, value: float, exchanger: str) -> dict:
        to_insert = {
            'token': token,
            'currency': currency,
            'value': value,
            'exchanger': exchanger,
            'timestamp': datetime.datetime.now().isoformat() + 'Z'
        }

        return to_insert
