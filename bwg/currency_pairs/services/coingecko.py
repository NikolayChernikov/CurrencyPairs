"""CoinGecko client module."""
import logging
import time
from pycoingecko import CoinGeckoAPI
from typing import Dict

__all__ = ("CoinGeckoService",)

logger = logging.getLogger(__name__)


class CoinGeckoService:
    """CoinGecko service."""

    def __init__(self) -> None:
        self.client = CoinGeckoAPI()

    def get_currency_by_pair(self, pairs: Dict) -> Dict:
        res = {}
        for token in pairs.keys():
            pair = self.client.get_price(ids=token, vs_currencies=pairs[token])
            time.sleep(0.2)
            res.update(pair)
        return res

    def ping(self):
        if self.client.ping():
            return True
