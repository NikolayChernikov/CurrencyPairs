""" Reverse URL service module. """
import logging
from typing import Any

from fastapi import FastAPI, Request

logger = logging.getLogger(__name__)


class ReverseUrlService:
    """Reverse Url service."""

    def __init__(self) -> None:
        self._app = None

    def init_app(self, app: FastAPI) -> None:
        self._app = app  # type: ignore[assignment]

    def url_for(
            self,
            endpoint_name: str,
            **kwargs: Any,
    ) -> str:
        return self._app.url_path_for(endpoint_name, **kwargs)  # type: ignore[attr-defined]

    @staticmethod
    def url_for_req(
            request: Request,
            endpoint_name: str,
            **kwargs: Any,
    ) -> str:
        return request.url_for(endpoint_name, **kwargs)  # type: ignore[return-value]
