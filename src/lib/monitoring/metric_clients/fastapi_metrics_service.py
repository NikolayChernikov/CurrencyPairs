""" Monitoring service module for fastapi metrics. """
# pylint: disable=broad-exception-caught, protected-access, too-many-arguments
import logging
from typing import Iterable

from src.lib.monitoring.prometheus_monitoring import (
    BaseMetric,
    BaseMetricName,
    BaseMetricsService,
    GaugeMetric,
    OperationType,
)

__all__ = ("FastapiMetricsService",)

logger = logging.getLogger(__name__)


class FastapiMetricsName(BaseMetricName):
    """Suffix for fastapi metric name."""

    ENDPOINT_LATENCY = "fastapi_endpoint_latency_seconds"


METRIC_ITEMS = (
    GaugeMetric(
        name=FastapiMetricsName.ENDPOINT_LATENCY.value,
        documentation="Metric for fastapi request response",
        unit="seconds",
        labelnames=["endpoint_name", "method", "response_code"],
        multiprocess_mode='max',
    ),
)


class FastapiMetricsService(BaseMetricsService):
    """
    Metrics service for fastapi metrics.
    """

    metrics_list: Iterable["BaseMetric"] = METRIC_ITEMS

    def record_fastapi(self, endpoint_name: str, method: str, latency: float, response_code: int) -> None:
        """
            Record fastapi request info.

            Args:
                endpoint_name (str): (Operation id)
                method (str): (GET, POST)
                latency (float): (elapsed time for response)
                response_code (int): (200, 4xx, 5xx)

            Returns:
                None
        """

        labels = self.prometheus_service.normalise_labels(
            {"endpoint_name": endpoint_name, "method": method, "response_code": response_code}
        )

        self.prometheus_service.record_metric_to_registry(
            metric_name=FastapiMetricsName.ENDPOINT_LATENCY,
            value=latency,
            labels=labels,
            operation_type=OperationType.SET,
        )
