"""Application module."""
import logging

from dependency_injector.wiring import Provide, inject

from src.currency_pairs.containers import create_container
from src.currency_pairs.services.processor import ProcessorService

__all__ = ("Application",)

logger = logging.getLogger(__name__)


class Application:
    """
    Application.

    Initializes container and runs event loop.
    """

    def __init__(self) -> None:
        """
        Init application.
        """
        self.container = create_container()

    @staticmethod
    @inject
    def run(
            processor: "ProcessorService" = Provide['processor'],
    ) -> None:
        processor.run_infinity_loop()
