""" DataStorage module. """
from collections import defaultdict
import logging
import threading
from typing import Any, Callable

__all__ = ("DataStorageService", )

logger = logging.getLogger(__name__)


class DataStorageService:
    """
        Data storage.
        Allows you to save data objects and call its methods in the sequel
    """

    _data_storage: dict[Any, dict[str, str]] = defaultdict(dict)
    stop_event = threading.Event()

    def add_item(self, data_name: str, identifier: Any, item: Any) -> None:
        self._data_storage[data_name][identifier] = item

    def remove_item(self, data_name: str, identifier: Any) -> None:
        if not self._data_storage[data_name] or not identifier:
            return

        self._data_storage[data_name].pop(identifier, None)
        if not self._data_storage[data_name]:
            del self._data_storage[data_name]

    def invoke_item_args(self, data_name: str, identifier: Any, method: Callable, args: tuple) -> Any:
        method_name = method.__name__
        item_method = getattr(self._data_storage[data_name][identifier], method_name)
        result = item_method(*args)
        return result

    def invoke_item_kwargs(self, data_name: str, identifier: str, method: Callable, kwargs: dict) -> Any:
        method_name = method.__name__
        item_method = getattr(self._data_storage[data_name][identifier], method_name)
        result = item_method(**kwargs)
        return result

    def get_item(self, data_name: str, identifier: Any) -> Any:
        if not self._data_storage[data_name] or not identifier:
            return None
        record = self._data_storage[data_name].get(identifier, None)
        return record

    def pop_item(self, data_name: str, identifier: Any) -> Any:
        if not self._data_storage[data_name] or not identifier:
            return None
        record = self._data_storage[data_name].pop(identifier, None)
        return record

    def update_item_attributes(self, data_name: str, identifier: Any, data: dict) -> None:
        if not self._data_storage[data_name] or not identifier:
            return
        for name, value in data.values():
            setattr(self._data_storage[data_name][identifier], name, value)
