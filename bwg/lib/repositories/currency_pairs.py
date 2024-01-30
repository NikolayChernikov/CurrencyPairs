"""Repository of the Spanner Task Engine Items Model."""
import logging

from bwg.lib.models.currency_pairs import CurrencyPairs
from bwg.lib.repositories.base import BaseRepository

__all__ = ("CurrencyPairsRepository",)

logger = logging.getLogger(__name__)


class CurrencyPairsRepository(BaseRepository):
    """Currency Pairs Repository."""

    Model = CurrencyPairs
