"""Transport monitoring module."""
# pylint: disable=too-many-arguments, broad-exception-caught, unnecessary-pass, too-many-arguments
# pylint: disable=super-with-arguments, protected-access
import logging
import threading
from typing import Any, Callable, Dict, Optional, TYPE_CHECKING, Union

from prometheus_client import CollectorRegistry, push_to_gateway

from .extensions.utils import delete_metric_from_registry
from .schedule import PeriodicTask

if TYPE_CHECKING:
    from .data_storage import DataStorageService

logger = logging.getLogger(__name__)


class PrometheusPeriodicMetricTask(PeriodicTask):
    """Prometheus thread that periodically calls a given function."""

    daemon = True

    def __init__(self, interval: Union[int, float] = None, function: Callable = None,
                 args: Any = None, kwargs: Any = None, name: str = None):

        self.func = function
        self.args = args
        self.kwargs = kwargs

        def func(*aa: Any, **kw: Any) -> None:
            try:
                return self.func(*aa, **kw)
            except Exception as ex:  # pragma: no cover
                logger.exception(f"Error handling metric export: {ex}")
                return None

        super(PrometheusPeriodicMetricTask, self).__init__(
            interval=interval, function=func, args=args, kwargs=kwargs, name=f'{name} Worker'
        )

    def close(self) -> None:
        """ Executes function and closes thread """
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as ex:
            logger.exception(f"Error handling metric flush: {ex}")
        self.cancel()


def get_exporter_thread(gateway: str, registry: CollectorRegistry, lock: threading.Lock, job: str,
                        data_storage: "DataStorageService",
                        grouping_key: Optional[Dict[str, Any]] = None,
                        interval: int = 60, push: bool = True,
                        use_metrics: bool = True,
                        ) -> PrometheusPeriodicMetricTask:  # pragma: no cover
    """Get a running task that periodically exports metrics.

    Args:
            gateway (str): the url for your push gateway
            registry (CollectorRegistry): metrics registry
            lock (threading.Lock): lock for removing old metrics from local registry
            job (str): metric job
            data_storage (DataStorageService): data manager for managing metrics duration and creation time
            grouping_key (Optional[Dict[str, Any]]): https://github.com/prometheus/pushgateway
            interval (int): interval between metrics push to gateway
            push (int): should data be pushed to gateway
            use_metrics (bool): enable metrics thread

    """

    def flush_metrics() -> None:  # pragma: no cover

        if not registry._collector_to_names:
            return

        if push:
            push_to_gateway(gateway=gateway, job=job, registry=registry, grouping_key=grouping_key)
            logger.debug("METRICS PUSHED")

        delete_metric_from_registry(registry=registry, data_storage=data_storage, lock=lock)

        return

    threads = threading.enumerate()
    export_threads_count = 0

    for th in threads[::-1]:
        if isinstance(th, PrometheusPeriodicMetricTask):
            export_threads_count += 1

    tt = PrometheusPeriodicMetricTask(
        interval=interval,
        function=flush_metrics,
        kwargs={},
        name=f"MetricsExporterThread_{export_threads_count + 1}"
    )
    if use_metrics:
        tt.start()
    return tt
