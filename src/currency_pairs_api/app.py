"""Application module."""
import logging

from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI

from src.currency_pairs_api.containers import create_container
from src.currency_pairs_api.endpoints.v1.test import router_test as test_router
from src.currency_pairs_api.logging_config import LOGGING_CONFIG
from src.currency_pairs_api.setup_logger import setup_logger

setup_logger(logging_config=LOGGING_CONFIG)

__all__ = ("create_app",)

logger = logging.getLogger(__name__)


class Application:
    """
    Application.

    Initializes container and runs event loop.
    """

    def __init__(self) -> None:
        self.container = create_container()

    @inject
    def create_api_app(
            self,
            fastapi_config: dict = Provide["config.fastapi"],
    ) -> FastAPI:
        app = FastAPI(title="Currency-Pairs", version="1")

        prefix = fastapi_config["prefix_v1"]

        app.include_router(test_router, prefix=prefix)

        app.container = self.container  # type: ignore[attr-defined]
        self.container.reverse_url().init_app(app)

        logger.info("Initialized Currency-Pairs API")
        return app


def create_app() -> FastAPI:
    application = Application()
    return application.create_api_app()
