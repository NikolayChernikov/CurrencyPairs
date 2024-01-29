"""Prometheus service module."""
# pylint: disable=too-many-instance-attributes, protected-access, unnecessary-pass, broad-exception-caught
# pylint: disable=method-hidden
from dataclasses import asdict, dataclass
import enum
import logging
import os
import threading
import time
from typing import Any, Dict, List, Literal, Optional, Sequence, Type, Union

import prometheus_client.gc_collector as pr_gc_collector
import prometheus_client.metrics as pr_metrics
import prometheus_client.platform_collector as pr_platform_collector
import prometheus_client.process_collector as pr_process_collector
import prometheus_client.registry as pr_registry

from .data_storage import DataStorageService
from .exporters import get_exporter
from .extensions import values

pr_metrics.values = values

__all__ = (
    "PrometheusService",
    "CounterMetric",
    "EnumMetric",
    "GaugeMetric",
    "HistogramMetric",
    "InfoMetric",
    "SummaryMetric",
    "OperationType",
    "BaseMetricName",
    "BaseMetric",
)

logger = logging.getLogger(__name__)


@dataclass
class BaseMetric:
    """Metric args."""

    name: str
    documentation: str
    labelnames: List[str]
    metric_type: Literal['counter', 'enum', 'gauge', 'histogram', 'info', 'summary']
    namespace: Optional[str]
    subsystem: Optional[str]


@dataclass
class HistogramMetric(BaseMetric):
    """Histogram metric args."""
    unit: Optional[Literal['seconds', 'ratio', 'bytes', 'ones']] = 'ones'
    metric_type: Literal['counter', 'enum', 'gauge', 'histogram', 'info', 'summary'] = 'histogram'
    buckets: Sequence[Union[float, str]] = (
        .005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0, pr_metrics.INF
    )
    namespace: Optional[str] = ''
    subsystem: Optional[str] = ''


@dataclass
class GaugeMetric(BaseMetric):
    """Gauge metric args."""
    unit: Optional[Literal['seconds', 'ratio', 'bytes', 'ones']] = 'ones'
    metric_type: Literal['counter', 'enum', 'gauge', 'histogram', 'info', 'summary'] = 'gauge'
    multiprocess_mode: Literal['min', 'max', 'livesum', 'liveall', 'all'] = 'all'
    namespace: Optional[str] = ''
    subsystem: Optional[str] = ''


@dataclass
class EnumMetric(BaseMetric):
    """Enum metric args."""
    metric_type: Literal['counter', 'enum', 'gauge', 'histogram', 'info', 'summary'] = "enum"
    states: Sequence[str] = ()
    namespace: Optional[str] = ''
    subsystem: Optional[str] = ''


@dataclass
class CounterMetric(BaseMetric):
    """Counter metric args."""
    unit: Optional[Literal['seconds', 'ratio', 'bytes', 'ones']] = 'ones'
    metric_type: Literal['counter', 'enum', 'gauge', 'histogram', 'info', 'summary'] = "counter"
    namespace: Optional[str] = ''
    subsystem: Optional[str] = ''


@dataclass
class InfoMetric(BaseMetric):
    """Info metric args."""
    metric_type: Literal['counter', 'enum', 'gauge', 'histogram', 'info', 'summary'] = "info"
    namespace: Optional[str] = ''
    subsystem: Optional[str] = ''


@dataclass
class SummaryMetric(BaseMetric):
    """Summary metric args."""
    unit: Optional[Literal['seconds', 'ratio', 'bytes', 'ones']] = 'ones'
    metric_type: Literal['counter', 'enum', 'gauge', 'histogram', 'info', 'summary'] = "summary"
    namespace: Optional[str] = ''
    subsystem: Optional[str] = ''


class OperationType(enum.Enum):
    """Operation type for different metric types."""
    # Counter, Gauge
    INCREMENT = "inc"
    # Gauge
    DECREMENT = "dec"
    # Gauge
    SET = "set"
    # Gauge
    SET_FUNCTION = "set_function"
    # Summary, Histogram
    OBSERVE = "observe"
    # Info
    INFO = "info"
    # Enum
    STATE = "state"


class BaseMetricName(enum.Enum):
    """Class for metrics names."""
    pass


class PrometheusService:
    """ Class for sending metrics to prometheus.
    """

    def __init__(self, config: dict[str, Any]) -> None:
        self.config = config
        self.registry = pr_metrics.CollectorRegistry()
        self.data_storage = DataStorageService()
        self._lock = threading.Lock()

        self.grouping_key = {
            'instance': os.environ.get('CONTAINER_NAME', 'default'),
            'env': config.get('environment', 'development'),
        }
        self.prefix = config.get('prefix', 'default')

        config['registry'] = self.registry
        config['lock'] = self._lock
        config['grouping_key'] = self.grouping_key
        config['data_storage'] = self.data_storage
        self.exporter = get_exporter(config=config, exporter_type=config['exporter_type'])

        if not config.get("use_default_metrics", False):
            self._unregister_default_metrics()

        # disable multiprocessing mode
        # if multiprocessing enabled, metrics will be duplicated
        # the first metric will be pushed to gateway with user set 'job' and the second (identical) with job 'fastapi'
        if config.get('disable_multiprocessing_mode', False):
            pr_metrics.values.ValueClass = pr_metrics.values.MutexValue

        if config['disable_service']:
            self.record_metric_to_registry = lambda *arg, **kw: None  # type: ignore[method-assign]
            self.export_metrics_manually = lambda *arg, **kw: None  # type: ignore[method-assign]
            return

    @classmethod
    def _unregister_default_metrics(cls) -> None:
        """ Unregister default metrics """
        default_metrics = (
            pr_gc_collector.GC_COLLECTOR,
            pr_process_collector.PROCESS_COLLECTOR,
            pr_platform_collector.PLATFORM_COLLECTOR
        )
        for metric in default_metrics:
            try:
                pr_registry.REGISTRY.unregister(metric)
            except KeyError:
                pass

    def export_metrics_manually(self) -> None:
        """ Manual metrics export """
        self.exporter.manual_export()

    def _get_metric_by_name(self, name: str) -> Type[pr_metrics.MetricWrapperBase]:
        """ Get metric collector from
        Args:
            name (str): base name of metric

        Returns:
            MetricWrapperBase
        """
        fullname = self._get_full_metric_name(name=name)
        return self.registry._names_to_collectors[fullname]  # type: ignore

    def _get_full_metric_name(self, name: str) -> str:
        """ Get full metric name
        Args:
            name (str): base name of metric

        Returns:
            str
        """
        return f'{self.prefix}_{name}'

    def get_metric_collector_instance_by_metric_info(self, metric_info: BaseMetric) -> pr_metrics.MetricWrapperBase:
        """ Get metric collector instance for further metric recording
        Args:
            metric_info (MetricArgs): instance with metric options

        Returns:
            MetricWrapperBase
        """

        metric_type_map = {
            "counter": pr_metrics.Counter,
            "enum": pr_metrics.Enum,
            "gauge": pr_metrics.Gauge,
            "histogram": pr_metrics.Histogram,
            "info": pr_metrics.Info,
            "summary": pr_metrics.Summary,
        }

        metric_info.namespace = self.prefix
        metric_info.labelnames = list(set(metric_info.labelnames))

        metric_collector: Type[pr_metrics.MetricWrapperBase] = metric_type_map[metric_info.metric_type]  # type: ignore
        kwargs = asdict(metric_info)
        del kwargs["metric_type"]

        base_info = {
            "name": self._get_full_metric_name(name=metric_info.name),
            "registry": None,
            **kwargs,
        }

        return metric_collector(**base_info)

    def record_metric_to_registry(self, metric_name: BaseMetricName, value: float,
                                  labels: Dict[str, str], operation_type: OperationType) -> None:
        """
                Record metric to local registry.

                Args:
                    metric_name (BaseMetricName): metric name
                    value (float): value to record
                    labels: metric labels
                    operation_type (OperationType): operation on metric - increment, decrement, etc

                Returns:
                    None
                """
        try:
            metric_collector = self._get_metric_by_name(name=metric_name.value)

            if not hasattr(metric_collector.__class__, operation_type.value):
                raise ValueError(f"Unsupported operation {operation_type} for class {metric_collector.__class__}")

            creation_timestamp = str(time.time())

            duration = labels.get("duration", None)

            if isinstance(duration, str):
                duration = "inf"
            elif isinstance(duration, (int, float)):
                duration = str(labels["duration"])
            else:
                duration = (
                    self.config["default_metric_duration"].get(f"{metric_collector.__class__.__name__}".lower(), 60)
                )

            with self._lock:
                if not metric_collector._labelvalues:
                    if labels.get("duration", None):
                        del labels["duration"]
                    metric_collector = metric_collector.labels(**labels)  # type: ignore
                    if self.config['auto_clear_metrics'] and duration != "inf":
                        self.data_storage.add_item(
                            data_name=f"{metric_collector._type}_{metric_collector._name}",
                            identifier=metric_collector._labelvalues,
                            item={"duration": duration, "creation_timestamp": creation_timestamp}
                        )
                method = getattr(metric_collector, operation_type.value)
                method(value)
            logger.info(f"Metric '{metric_name.value}' recorded with {value=} and labels {labels=}")
        except Exception as exc:
            logger.exception(f"Failed record metric to registry with exception: {exc}")

    @classmethod
    def normalise_labels(cls, labels: dict) -> dict:
        """
        Adjust labels values to str.

        Args:
            labels (dict): labels to adjust

        Returns:
            dist
        """

        normalised_labels = {str(k): str(v) for k, v in labels.items()}
        return normalised_labels
