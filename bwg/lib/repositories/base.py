"""Base Repository for the Spanner Models."""
import logging
from typing import TYPE_CHECKING, Any, ClassVar, Optional, Type

from sqlalchemy import orm
from sqlalchemy.inspection import inspect

if TYPE_CHECKING:
    from sqlalchemy.ext.declarative.api import DeclarativeMeta

__all__ = ("BaseRepository",)

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base Repository.

    Provides CRUD methods for the objects of type Model.
    """

    Model: ClassVar[Type["DeclarativeMeta"]]

    def insert_or_update(self, session: orm.Session, **kwargs: Any) -> "DeclarativeMeta":
        cancelled_label_object = session.query(self.Model).filter_by(**kwargs).with_for_update().one_or_none()
        if cancelled_label_object is None:
            cancelled_label_object = self.Model(**kwargs)

        return session.merge(cancelled_label_object)

    def get_row(self, session: orm.Session, token: str, currency: str) -> Optional["DeclarativeMeta"]:
        return session.query(self.Model).select_from(self.Model).filter_by(
            token=token,
            currency=currency).first()

    @classmethod
    def model_as_dict(cls, model: "DeclarativeMeta") -> dict:
        return {c.key: getattr(model, c.key)
                for c in inspect(model).mapper.column_attrs}
