"""Postgres Database module."""
import logging

from bwg.lib.database import Database

__all__ = ("PostgresDatabase",)

logger = logging.getLogger(__name__)


class PostgresDatabase(Database):
    """Postgres Database."""
