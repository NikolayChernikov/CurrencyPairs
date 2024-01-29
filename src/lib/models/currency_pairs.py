"""EntityTableType module."""
from sqlalchemy import Column, DateTime, String, Float

from src.lib.models.base import Base

__all__ = ("CurrencyPairs",)


class CurrencyPairs(Base):
    """CurrencyPairs model."""
    __tablename__ = "currency_pairs"

    token = Column(String(20), primary_key=True)
    currency = Column(String(20), primary_key=True)
    value = Column(Float(50), nullable=False)
    timestamp = Column(DateTime, nullable=False)
