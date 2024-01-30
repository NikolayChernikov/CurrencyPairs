"""CoinGecko client module."""
import logging
from binance.client import Client
from typing import Dict

__all__ = ("BinanceService",)

logger = logging.getLogger(__name__)


class BinanceService:
    """Binance service."""

    def __init__(self) -> None:
        self.client = Client()

    def get_currency_by_pair(self) -> Dict:
        tickers = self.client.get_symbol_ticker()

    def ping(self):
        try:
            self.client.ping()
        except Exception:
            return False
        else:
            return True
