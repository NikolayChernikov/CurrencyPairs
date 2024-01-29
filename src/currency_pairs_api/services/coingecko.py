"""CoinGeko client module."""
import logging
from pycoingecko import CoinGeckoAPI
from typing import Dict

__all__ = ("CoinGeckoService",)

logger = logging.getLogger(__name__)


class CoinGeckoService:
    """CoinGecko service."""

    def __init__(self) -> None:
        self.client = CoinGeckoAPI()
        self.token_compendium = {
            'btc': 'bitcoin',
            'eth': 'ethereum',
        }
        self.currency_compendium = {
            'rub': 'rub',
            'usd': 'usd',
        }

    def get_currency_by_pair(self, token: str, currency: str) -> None:
        pair = self.client.get_price(ids=token, vs_currencies=currency)
        return pair
