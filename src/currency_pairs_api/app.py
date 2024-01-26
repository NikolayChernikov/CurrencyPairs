"""Application module."""
from dependency_injector.wiring import inject, Provide
from fastapi import FastAPI

from src.currency_pairs_api.containers import create_container
from src.currency_pairs_api.endpoints.v1.test import router_test as test_router

__all__ = ("create_app",)


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

        return app


def create_app() -> FastAPI:
    application = Application()
    return application.create_api_app()
