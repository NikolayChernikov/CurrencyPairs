"""Application module."""
import logging

from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI

from currency_pairs.container import create_container
from currency_pairs.endpoints.v1.test import router_test as test_router


__all__ = ("create_app",)

logger = logging.getLogger(__name__)


class Application:

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

        app.container = self.container
        self.container.reverse_url().init_app(app)

        logger.info("Initialized Currency-Pairs API")
        return app


def create_app() -> FastAPI:
    application = Application()
    return application.create_api_app()
