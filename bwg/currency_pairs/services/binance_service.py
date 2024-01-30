"""CoinGecko client module."""
# pylint: disable=consider-iterating-dictionary
# pylint: disable=broad-exception-caught
import logging
import time
from typing import Dict

from binance.client import Client

__all__ = ("BinanceService",)

logger = logging.getLogger(__name__)


class BinanceService:
    """Binance service."""

    def __init__(self) -> None:
        self.client = Client()
        self.compendium = {
            'USDT': 'USD',
            'RUB': 'RUB'
        }

    def get_currency_by_pair(self, pairs:  Dict) -> dict:
        res = {}
        for token in pairs.keys():
            token_buffer = {}  # type: ignore[var-annotated]
            for currency in pairs[token]:
                symbol = token+currency
                tickers = self.client.get_symbol_ticker(symbol=symbol)
                if token not in token_buffer.keys():
                    token_buffer[str(token)] = {self.compendium[currency]: tickers['price']}
                else:
                    token_buffer[str(token)].update({self.compendium[currency]: tickers['price']})
                res.update(token_buffer)
            time.sleep(0.2)
        return res

    def ping(self) -> bool:
        try:
            self.client.ping()
        except Exception:
            return False
        return True
