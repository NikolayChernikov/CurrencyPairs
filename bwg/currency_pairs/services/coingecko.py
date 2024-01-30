"""CoinGecko client module."""
import logging
from pycoingecko import CoinGeckoAPI
from typing import Dict

__all__ = ("CoinGeckoService",)

logger = logging.getLogger(__name__)


class CoinGeckoService:
    """CoinGecko service."""

    def __init__(self) -> None:
        self.client = CoinGeckoAPI()
        self.tokens = ['bitcoin', 'ethereum']
        self.currencies = ['rub', 'usd']

    def get_currency_by_pair(self) -> Dict:
        pair = self.client.get_price(ids=self.tokens, vs_currencies=self.currencies)
        return pair
