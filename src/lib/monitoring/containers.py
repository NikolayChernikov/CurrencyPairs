"""Monitoring container module."""
# pylint: disable=unsubscriptable-object
import logging

from dependency_injector import containers
from dependency_injector.providers import Dependency, Singleton

from src.lib.monitoring import FastapiMetricsService
from src.lib.monitoring.prometheus_monitoring import PrometheusService

__all__ = ("MonitoringContainer",)

logger = logging.getLogger(__name__)


class MonitoringContainer(containers.DeclarativeContainer):
    """Monitoring package container."""

    config = Dependency()  # type: ignore[var-annotated]

    prometheus_service: Singleton[PrometheusService] = Singleton(
        PrometheusService,
        config=config.provided['asgi_monitoring'],
    )

    fastapi_metrics_service: Singleton[FastapiMetricsService] = Singleton(
        FastapiMetricsService,
        prometheus_service=prometheus_service,
    )
