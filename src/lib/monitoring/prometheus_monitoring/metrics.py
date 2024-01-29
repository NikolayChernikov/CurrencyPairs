"""Monitoring module with custom metrics."""
# pylint: disable=broad-exception-caught, protected-access, too-many-arguments
import logging
from typing import Iterable

from .prometheus import BaseMetric, PrometheusService

__all__ = ("BaseMetricsService", )

logger = logging.getLogger(__name__)


METRIC_ITEMS = ()


class BaseMetricsService:
    """
    Metrics service.
    """

    metrics_list: Iterable["BaseMetric"] = METRIC_ITEMS

    def __init__(self, prometheus_service: "PrometheusService"):
        """Init service."""
        self.prometheus_service = prometheus_service
        self._register_metrics()

    def _register_metrics(self) -> None:
        """ Registers metric to local registry. """

        if not self.metrics_list:
            logger.warning("Metrics list is empty")

        for metric in self.metrics_list:
            try:
                metric_collector_instance = (
                    self.prometheus_service.get_metric_collector_instance_by_metric_info(metric_info=metric)
                )
                self.prometheus_service.registry.register(metric_collector_instance)
            except Exception as exc:
                logger.exception((f"Can't register metric: {metric}", f"Exception: {exc}"))
