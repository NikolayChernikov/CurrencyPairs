"""Postgres Database module."""
import logging

from src.lib.database import Database

__all__ = ("PostgresDatabase",)

logger = logging.getLogger(__name__)


class PostgresDatabase(Database):
    """Postgres Database."""
