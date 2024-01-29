""" Extensions module."""
# pylint: disable=protected-access
import logging
import mmap
import struct
import threading
import time

from prometheus_client import CollectorRegistry
from prometheus_client.mmap_dict import _pack_integer, MmapedDict
from prometheus_client.multiprocess import MultiProcessCollector

from ..data_storage import DataStorageService

logger = logging.getLogger(__name__)

__all__ = ("delete_key", "delete_metric_from_registry",)


def delete_key(self: MmapedDict, key: str) -> None:
    """
        extension for mmap_dict.py of prometheus
        deletes metric key and value from files that are used in multiprocess mode
    """
    if key not in self._positions:
        return
    value_start_pos = self._positions[key]
    encoded = key.encode('utf-8')
    # Pad to be 8-byte aligned.
    padded = encoded + (b' ' * (8 - (len(encoded) + 4) % 8))
    value = struct.pack(f'i{len(padded)}sd'.encode(), len(encoded), padded, 0.0)
    self._capacity = self._capacity - len(value)
    left_data, right_data = self._m[0:value_start_pos + 8 - len(value)], self._m[value_start_pos + 8:]
    # clear old data
    self._f.truncate(0)
    self._f.truncate(self._capacity)
    self._m = mmap.mmap(self._f.fileno(), self._capacity)
    self._m.write(left_data)
    self._m.write(right_data)

    # Update how much space we've used.
    self._used -= len(value)
    _pack_integer(self._m, 0, self._used)
    del self._positions[key]

    # update keys that are written after deleted key
    for k, v in self._positions.items():
        if v > value_start_pos:
            self._positions[k] = v - len(value)


def delete_metric_from_registry(registry: CollectorRegistry,
                                data_storage: "DataStorageService", lock: threading.Lock) -> None:
    """
        extension for metrics.py of prometheus
        deletes metrics with certain labels from local registry

        each item's to delete 'duration' and 'creation_time' must be added to data_storage to have item deleted

        Args:
            registry (CollectorRegistry): prometheus CollectorRegistry
            data_storage (DataStorageService) storege for temporary 'duration' and 'creation_time' keeping
            lock (threading.Lock): lock for deletion from registry
    """

    for parent_collector in registry._collector_to_names.keys():

        if isinstance(parent_collector, MultiProcessCollector):
            continue

        for metric in tuple(parent_collector._metrics.values()):  # type: ignore[attr-defined]
            if not metric._labelvalues:
                continue

            logger.debug(parent_collector._metrics)  # type: ignore[attr-defined]

            try:

                item = data_storage.get_item(
                    data_name=f"{parent_collector._type}_{parent_collector._name}",  # type: ignore[attr-defined]
                    identifier=metric._labelvalues,
                )

                if item is None:
                    continue

                value = metric._value  # see in MultiProcessValue -> MmapedValue of extension.values

                logger.debug(f"Collector lifecycle info: {item}")

                if (float(item['creation_timestamp']) +
                        float(item['duration']) < time.time()):
                    value.delete()  # deletion from multiprocess files

                    with lock:
                        parent_collector.remove(*metric._labelvalues)  # type: ignore[attr-defined]
                        data_storage.remove_item(
                            data_name=f"{parent_collector._type}_{parent_collector._name}",  # type: ignore
                            identifier=metric._labelvalues,
                        )

                    logger.debug("METRIC DELETED FROM REGISTRY")
            except ValueError:
                # metric duration is infinite
                pass
