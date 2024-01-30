import logging
import time
import datetime
from typing import Optional
from bwg.currency_pairs.services.coingecko import CoinGeckoService
from bwg.lib.postgres import PostgresDatabase
from bwg.lib.repositories.currency_pairs import CurrencyPairsRepository
from bwg.currency_pairs.services.binance_service import BinanceService

__all__ = ("ProcessorService",)

logger = logging.getLogger(__name__)


class ProcessorService:
    """Processor service."""

    coingecko: "CoinGeckoService"
    binance: "BinanceService"
    db_postgres: "PostgresDatabase"
    currency_pairs_repository: "CurrencyPairsRepository"

    bitcoin_pairs = {
        'BTC': ['RUB', 'USDT'],
        'ETH': ['RUB', 'USDT'],
    }

    coingecko_pairs = {
        'BITCOIN': ['RUB', 'USD'],
        'ETHEREUM': ['RUB', 'USD'],
    }

    def run_infinity_loop(self):
        try:
            logger.info("Run infinity loop")
            while True:
                exchaner = 'coingecko'
                with self.db_postgres.session() as session:
                    if exchaner == 'coingecko':
                        pairs = self.coingecko.get_currency_by_pair(self.coingecko_pairs)
                        for token in pairs.keys():
                            for currency in pairs[token].keys():
                                value = pairs[token][currency]
                                to_insert = self.make_msg(token, currency, value, exchaner)
                                self.currency_pairs_repository.insert_or_update(session, **to_insert)
                                session.commit()
                    elif exchaner == 'binance':
                        ...
                    time.sleep(5)

        except Exception as exc:
            logger.exception(f"Failed with {exc=}.")

    def exchanges_selector(self) -> Optional[str]:
        while True:
            if self.coingecko.ping():
                return 'coingecko'
            elif self.binance.ping():
                return 'binance'
            else:
                logger.error("Could not connect to exchanges")
                time.sleep(60)

    @staticmethod
    def make_msg(token, currency, value, exchanger):
        to_insert = {
            'token': token,
            'currency': currency,
            'value': value,
            'exchanger': exchanger,
            'timestamp': datetime.datetime.now().isoformat() + 'Z'
        }

        return to_insert
