"""Currency pairs service module."""
import logging
from src.lib.repositories.currency_pairs import CurrencyPairsRepository
from src.lib.postgres.database import PostgresDatabase
from fastapi import HTTPException
from starlette.status import HTTP_404_NOT_FOUND

__all__ = ("CurrencyPairsService",)

logger = logging.getLogger(__name__)


class CurrencyPairsService:
    """Currency Pairs service."""

    currency_pairs_repository: "CurrencyPairsRepository"
    db_postgres: "PostgresDatabase"

    def __init__(self) -> None:
        self.token_compendium = {
            'btc': 'bitcoin',
            'eth': 'ethereum',
        }
        self.invert_token_compendium = {v: k for k, v in self.token_compendium.items()}
        self.currency_compendium = ['rub', 'usd']

    def execute(self, token, currency):
        self.validate_pair(token, currency)
        with self.db_postgres.session() as session:
            result = self.currency_pairs_repository.get_row(session=session,
                                                            token=self.token_compendium[token.lower()],
                                                            currency=currency.lower())
            if result:
                dict_result = self.currency_pairs_repository.model_as_dict(result)
                return self.format_msg(dict_result['token'], dict_result['currency'], dict_result['value'])

    def validate_pair(self, token: str, currency: str) -> None:
        if token.lower() not in self.token_compendium.keys():
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail={
                    "message": f"Token not found. Available tokens: {list(self.token_compendium.keys())}",
                }
            )
        elif currency.lower() not in self.currency_compendium:
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail={
                    "message": f"Currency not found. Available currencies: {self.currency_compendium}",
                }
            )

    def format_msg(self, token: str, currency: str, value: float):
        return {
            "exchanger": "coingecko",
            "cources": [
                {
                    "direction": f"{self.invert_token_compendium[token.lower()]}-{currency}".upper(),
                    "value": value
                }
            ]
        }
