"""Application module."""
import logging

from dependency_injector.wiring import Provide, inject
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.currency_pairs_api.containers import create_container
from src.currency_pairs_api.endpoints.v1.currency_pairs import \
    currency_pairs_router
from src.currency_pairs_api.endpoints.v1.test import router_test as test_router
from src.currency_pairs_api.logging_config import LOGGING_CONFIG
from src.lib.setup_logger import setup_logger
from src.lib.monitoring import FastapiMetricsService
from src.currency_pairs_api.middleware import MetricsMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic_core import ValidationError
from src.currency_pairs_api.exception_handlers import pydantic_validation_error_exception_handler


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
            api_config: dict = Provide["config.api"],
            fastapi_config: dict = Provide["config.fastapi"],
            metrics_client: "FastapiMetricsService" = Provide["monitoring_container.fastapi_metrics_service"]
    ) -> FastAPI:
        app = FastAPI(title="Currency-Pairs", version="1")

        prefix = fastapi_config["prefix_v1"]

        app.include_router(test_router, prefix=prefix)
        app.include_router(currency_pairs_router, prefix=prefix)

        metrics_middleware = MetricsMiddleware(metrics_client=metrics_client, routes=app.routes)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=api_config["origins"],
            allow_credentials=True,
            allow_methods=["GET", "POST"],
            allow_headers=["*"],
        )
        metrics_app = metrics_client.prometheus_service.exporter.get_metrics_app()
        app.mount("/metrics", metrics_app)
        app.add_middleware(BaseHTTPMiddleware, dispatch=metrics_middleware)

        app.add_exception_handler(ValidationError, pydantic_validation_error_exception_handler)

        app.container = self.container  # type: ignore[attr-defined]
        self.container.reverse_url().init_app(app)

        logger.info("Initialized Currency-Pairs API")
        return app


def create_app() -> FastAPI:
    application = Application()
    return application.create_api_app()
