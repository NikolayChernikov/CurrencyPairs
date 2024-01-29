import logging
import time
import datetime
from src.currency_pairs.services.coingecko import CoinGeckoService
from src.lib.postgres import PostgresDatabase
from src.lib.repositories.currency_pairs import CurrencyPairsRepository

__all__ = ("ProcessorService",)

logger = logging.getLogger(__name__)


class ProcessorService:
    """Processor service."""

    coingecko: "CoinGeckoService"
    db_postgres: "PostgresDatabase"
    currency_pairs_repository: "CurrencyPairsRepository"

    pairs = {
        'BTC': ['rub', 'usd'],
        'ETH': ['rub', 'usd'],
    }

    def run_infinity_loop(self):
        try:
            logger.info("Run infinity loop")
            while True:
                with self.db_postgres.session() as session:
                    pairs = self.coingecko.get_currency_by_pair()
                    for token in pairs.keys():
                        for currency in pairs[token].keys():
                            to_insert = {
                                'token': token,
                                'currency': currency,
                                'value': pairs[token][currency],
                                'timestamp': datetime.datetime.now().isoformat() + 'Z'
                            }

                            self.currency_pairs_repository.create_or_update(session, **to_insert)
                            session.commit()
                    time.sleep(5)
        except Exception as exc:
            logger.exception(f"Failed with {exc=}.")
