"""Currency pairs service module."""
import logging
from src.lib.repositories.currency_pairs import CurrencyPairsRepository
from src.lib.postgres.database import PostgresDatabase

__all__ = ("CurrencyPairsService",)

logger = logging.getLogger(__name__)


class CurrencyPairsService:
    """Currency Pairs service."""

    currency_pairs_repository: "CurrencyPairsRepository"
    db_postgres: "PostgresDatabase"

    def execute(self, token, currency):
        with self.db_postgres.session() as session:
            result = self.currency_pairs_repository.get_row(session=session,
                                                            token=token,
                                                            currency=currency)
            if result:
                return self.currency_pairs_repository.model_as_dict(result)
