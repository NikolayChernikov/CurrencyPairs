from sqlalchemy import create_engine, Column, Float, DateTime, String
from sqlalchemy.orm import declarative_base

engine = create_engine('postgresql+psycopg2://user:password@postgres/db')

Base = declarative_base(engine)


class CurrencyPairs(Base):
    """CurrencyPairs model."""
    __tablename__ = "currency_pairs"

    token = Column(String(20), primary_key=True)
    currency = Column(String(20), primary_key=True)
    value = Column(Float(50), nullable=False)
    exchanger = Column(String(20), primary_key=True)
    timestamp = Column(DateTime, nullable=False)
