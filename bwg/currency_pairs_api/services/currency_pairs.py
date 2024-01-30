"""Currency pairs service module."""
import logging
import dateutil.parser
from bwg.lib.repositories.currency_pairs import CurrencyPairsRepository
from bwg.lib.postgres.database import PostgresDatabase
from fastapi import HTTPException
from typing import Dict
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY, HTTP_500_INTERNAL_SERVER_ERROR

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
                self.currency_compendium.append(dict_result['timestamp'])

                return self.format_msg(dict_result['token'], dict_result['currency'],
                                       dict_result['value'], dict_result['exchanger'])

    def validate_pair(self, token: str, currency: str) -> None:
        if token.lower() not in self.token_compendium.keys():
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": f"Token not found. Available tokens: {list(self.token_compendium.keys())}",
                }
            )
        elif currency.lower() not in self.currency_compendium:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": f"Currency not found. Available currencies: {self.currency_compendium}",
                }
            )

    def format_msg(self, token: str, currency: str, value: float, exchanger: str) -> Dict:
        return {
            "exchanger": exchanger,
            "cources": [
                {
                    "direction": f"{self.invert_token_compendium[token.lower()]}-{currency}".upper(),
                    "value": value
                }
            ]
        }

    @staticmethod
    def check_if_data_expired(date):
        delta = dateutil.parser.isoparse(date) - dateutil.parser.isoparse(date)
        if delta.seconds > 5:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "message": "Server stores irrelevant data",
                }
            )
