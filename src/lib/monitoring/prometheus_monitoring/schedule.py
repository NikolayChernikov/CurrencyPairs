"""Periodic task module."""
# pylint: disable=too-many-arguments, super-with-arguments
from logging import getLogger
import threading
import time
from typing import Any, Callable, Optional, Union

logger = getLogger(__name__)


class PeriodicTask(threading.Thread):
    """Thread that periodically calls a given function."""

    def __init__(self, interval: Union[int, float], function: Callable,
                 args: Any = None, kwargs: Any = None, name: str = None):
        super(PeriodicTask, self).__init__(name=name)
        self.interval = interval
        self.function = function
        self.args = args or []
        self.kwargs = kwargs or {}
        self.finished = threading.Event()

    def run(self) -> None:
        """ Starts execute function periodically """
        wait_time = self.interval
        while not self.finished.wait(wait_time):
            start_time = time.time()
            self.function(*self.args, **self.kwargs)
            elapsed_time = time.time() - start_time
            wait_time = max(self.interval - elapsed_time, 0)

    def join(self, timeout: Optional[float] = None) -> None:
        self.function(*self.args, **self.kwargs)
        super().join(timeout=timeout)

    def cancel(self) -> None:
        """ Stops periodic function execution"""
        self.finished.set()
