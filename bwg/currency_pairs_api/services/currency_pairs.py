"""Currency pairs service module."""
import datetime
import logging

import dateutil.parser
from fastapi import HTTPException
from starlette.status import (HTTP_422_UNPROCESSABLE_ENTITY,
                              HTTP_502_BAD_GATEWAY)

from bwg.lib.postgres.database import PostgresDatabase
from bwg.lib.repositories.currency_pairs import CurrencyPairsRepository

__all__ = ("CurrencyPairsService",)

logger = logging.getLogger(__name__)


class CurrencyPairsService:
    """Currency Pairs service."""

    currency_pairs_repository: "CurrencyPairsRepository"
    db_postgres: "PostgresDatabase"

    def __init__(self) -> None:
        self.token_compendium = ['BTC', 'ETH']
        self.currency_compendium = ['RUB', 'USD']

    def execute(self, token: str, currency: str) -> dict:
        token = token.upper()
        currency = currency.upper()

        self.validate_pair(token, currency)
        with self.db_postgres.session() as session:  # type: ignore[var-annotated]
            result = self.currency_pairs_repository.get_row(session=session,
                                                            token=token,
                                                            currency=currency)
            if result:
                dict_result = self.currency_pairs_repository.model_as_dict(result)
                self.check_if_data_expired(dict_result['timestamp'])

                return self.format_msg(dict_result['token'], dict_result['currency'],
                                       dict_result['value'], dict_result['exchanger'])
        return {}

    def validate_pair(self, token: str, currency: str) -> None:
        if token not in self.token_compendium:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": f"Token not found. Available tokens: {self.token_compendium}",
                }
            )
        if currency not in self.currency_compendium:
            raise HTTPException(
                status_code=HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "message": f"Currency not found. Available currencies: {self.currency_compendium}",
                }
            )

    @staticmethod
    def format_msg(token: str, currency: str, value: float, exchanger: str) -> dict:
        return {
            "exchanger": exchanger,
            "cources": [
                {
                    "direction": f"{token}-{currency}",
                    "value": value
                }
            ]
        }

    @staticmethod
    def check_if_data_expired(date) -> None:  # type: ignore[no-untyped-def]
        current_time = datetime.datetime.now().isoformat() + 'Z'
        date = str(date)+'Z'
        delta = dateutil.parser.isoparse(current_time) - dateutil.parser.isoparse(date)
        if delta.seconds > 5:
            raise HTTPException(
                status_code=HTTP_502_BAD_GATEWAY,
                detail={
                    "message": "Server stores irrelevant data",
                }
            )
