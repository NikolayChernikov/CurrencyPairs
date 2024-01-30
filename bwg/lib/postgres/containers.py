"""Spanner component container module."""
# pylint: disable=[no-member, unsubscriptable-object]
import logging

from dependency_injector import containers, providers

from .database import PostgresDatabase

__all__ = ("PostgresContainer",)

logger = logging.getLogger(__name__)


class PostgresContainer(containers.DeclarativeContainer):
    """Spanner package container."""

    # config provided for the component
    config = providers.Dependency()  # type: ignore[var-annotated]

    # database layer sqlalchemy
    db = providers.Singleton(
        PostgresDatabase,
        db_dsn=config.provided["dsn"],
    )
