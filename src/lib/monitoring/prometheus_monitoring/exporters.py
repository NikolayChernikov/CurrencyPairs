""" Several metrics exporters module. """
from abc import ABC, abstractmethod
import functools
import logging
from typing import Any

from fastapi import APIRouter
from prometheus_client import make_asgi_app, multiprocess, push_to_gateway

from .transport import get_exporter_thread

__all__ = ("get_exporter", "BaseExporter", "FastapiExporter", "GatewayExporter")

logger = logging.getLogger(__name__)


class BaseExporter(ABC):
    """ Exporter abstract class """
    def __init__(self, config: dict):
        self.config = config

    @abstractmethod
    def get_metrics_app(self) -> Any:
        pass

    @abstractmethod
    def manual_export(self) -> None:
        pass


class FastapiExporter(BaseExporter):
    """ FastAPI exporter """
    def __init__(self, config: dict):
        super().__init__(config)

        kwargs = {
            "gateway": "",
            "registry": config['registry'],
            "lock": config['lock'],
            "job": config['job'],
            "grouping_key": config['grouping_key'],
            "interval": config['interval'],
            "data_storage": config['data_storage'],
        }

        if config['auto_clear_metrics'] and not self.config['disable_service']:
            self.cleaner_thread = get_exporter_thread(push=False, **kwargs)
        self.registry = config['registry']

    def get_metrics_app(self) -> Any:
        if self.config['disable_service']:
            metrics_router = APIRouter()

            @metrics_router.get("/")
            def metrics() -> dict:
                return {"message": "Fastapi metrics are disabled"}

            return metrics_router
        multiprocess.MultiProcessCollector(self.registry)
        return make_asgi_app(registry=self.registry)

    def manual_export(self) -> None:
        logger.warning(f"{type(self).__name__} doesn't provide manual export implementation")


class GatewayExporter(BaseExporter):
    """ Exporter for PushGateway """
    def __init__(self, config: dict):
        super().__init__(config)
        self.registry = config['registry']

        kwargs = {
            "gateway": config['gateway'],
            "registry": config['registry'],
            "lock": config['lock'],
            "job": config['job'],
            "grouping_key": config['grouping_key'],
            "interval": config['interval'],
            "data_storage": config['data_storage'],
            "use_metrics": config['use_metrics'],
        }

        self.client_partial = lambda *arg, **kw: None

        if not self.config['disable_service']:
            self.exporter_thread = get_exporter_thread(push=True, **kwargs)

            self.client_partial = functools.partial(
                push_to_gateway,
                job=config['job'],
                gateway=config['gateway'],
                grouping_key=config['grouping_key'],
                registry=self.registry,
            )

    def get_metrics_app(self) -> Any:
        logger.warning(f"{type(self).__name__} doesn't provide metrics app implementation")

    def manual_export(self) -> None:
        self.client_partial()


def get_exporter(config: dict, exporter_type: str) -> BaseExporter:
    if exporter_type == 'gateway':
        return GatewayExporter(config=config)
    if exporter_type == 'asgi':
        return FastapiExporter(config=config)
    raise ValueError(f"Unknown exporter type: {exporter_type}")
