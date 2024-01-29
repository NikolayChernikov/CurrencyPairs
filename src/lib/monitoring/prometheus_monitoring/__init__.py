# pylint: disable=expression-not-assigned, missing-module-docstring
import os
from pathlib import Path

from .metrics import BaseMetricsService
from .prometheus import (
    BaseMetric,
    BaseMetricName,
    CounterMetric,
    EnumMetric,
    GaugeMetric,
    HistogramMetric,
    InfoMetric,
    OperationType,
    PrometheusService,
    SummaryMetric,
)

__all__ = (
    'BaseMetric',
    'BaseMetricsService',
    'BaseMetricName',
    'CounterMetric',
    'EnumMetric',
    'GaugeMetric',
    'HistogramMetric',
    'InfoMetric',
    'OperationType',
    'PrometheusService',
    'SummaryMetric',
)

if 'PROMETHEUS_MULTIPROC_DIR' in os.environ:
    multiproc_dir = os.environ['PROMETHEUS_MULTIPROC_DIR']
    os.makedirs(multiproc_dir, exist_ok=True)
    [f.unlink() for f in Path(multiproc_dir).glob("*") if f.is_file()]  # type: ignore[func-returns-value]
