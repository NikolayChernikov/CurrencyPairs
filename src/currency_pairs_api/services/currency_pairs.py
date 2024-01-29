"""Currency pairs service module."""
import logging

from typing import Tuple
from src.currency_pairs_api.services.coingecko import CoinGeckoService
from fastapi import HTTPException
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

__all__ = ("CurrencyPairsService",)

logger = logging.getLogger(__name__)


class CurrencyPairsService:
    """CoinGecko service."""

    coingecko: "CoinGeckoService"

    def execute(self, token, currency):
        self.validate_data(token, currency)
        token, currency = self.unpack_value(token, currency)
        return self.coingecko.get_currency_by_pair(token, currency)

    def validate_data(self, token, currency):
        if token.lower() not in self.coingecko.token_compendium.keys():
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unexpected token. Available tokens: {list(self.coingecko.token_compendium.keys())}")
        if currency.lower() not in self.coingecko.currency_compendium.keys():
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Unexpected currency. Available currencies: {list(self.coingecko.currency_compendium.keys())}")

    def unpack_value(self, token, currency) -> Tuple[str, str]:
        token = self.coingecko.token_compendium[token.lower()]
        currency = self.coingecko.currency_compendium[currency.lower()]

        return token, currency
