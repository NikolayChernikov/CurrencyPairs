# pylint: disable=protected-access
"""Database module."""
import datetime
import logging
from contextlib import AbstractContextManager, contextmanager
from typing import Any, Callable, Optional

from sqlalchemy import create_engine, orm
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

__all__ = ("Database",)

logger = logging.getLogger(__name__)


class Database:
    """Database for ORM Models."""

    def __init__(
            self,
            db_dsn: str,
            execution_options: Optional[dict] = None,
            enable_logging: bool = False,
            **kwargs: Any,
    ) -> None:
        if execution_options is None:
            execution_options = {}

        read_only_execution_options = dict(
            execution_options or {},
            read_only=True,
            staleness=kwargs.get("staleness") or {"exact_staleness": datetime.timedelta(seconds=2)},
        )

        self._engine = self._create_engine(db_dsn, enable_logging, execution_options, **kwargs)
        self._read_only_engine = self._create_engine(db_dsn, enable_logging, read_only_execution_options, **kwargs)

        self._session_factory = self._create_session_factory(self._engine)
        self._read_only_session_factory = self._create_session_factory(self._read_only_engine)

    @staticmethod
    def _create_engine(db_dsn: str, enable_logging: bool, execution_options: dict, **kwargs: Any) -> Engine:
        return create_engine(
            db_dsn,
            echo=enable_logging,
            execution_options=execution_options,
            pool_size=50,
            pool_timeout=1800,
            **kwargs,
        )

    @staticmethod
    def _create_session_factory(bind_engine: Engine) -> sessionmaker:
        return orm.sessionmaker(
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            bind=bind_engine,
        )

    @contextmanager  # type: ignore[arg-type]
    def session(  # type: ignore[misc]
            self,
            autocommit: bool = False,
            read_only: bool = False
    ) -> Callable[..., AbstractContextManager[Session]]:
        """
        Session management.

        Returns:
            Session: created database session
        """
        if read_only:
            session: Session = self._read_only_session_factory(
                autocommit=autocommit,
            )
        else:
            session: Session = self._session_factory(  # type: ignore[no-redef]
                autocommit=autocommit,
            )
        try:
            yield session
        except Exception:
            logger.exception("Session rollback because of exception")
            session.rollback()
            raise
        finally:
            session.close()

    def close(self) -> None:
        """
        Close database.
        Returns:
            None
        """
        self._engine.dispose()
