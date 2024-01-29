"""Monitoring metrics executor module for usage with Celery"""
# pylint: disable=broad-exception-caught
from dataclasses import dataclass
from logging import getLogger
import multiprocessing
import queue
import threading
import time
from typing import Any, Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from .metrics import BaseMetricsService

__all__ = ("MetricsExecutor", )


logger = getLogger(__name__)


@dataclass
class Task:
    """Task."""

    func_name: str
    args: Tuple
    kwargs: Dict[str, Any]


class MetricsWorker:
    """Thread worker."""

    QUEUE_TIMEOUT = 3

    @classmethod
    def run(cls, metrics_client: "BaseMetricsService",
            task_queue: multiprocessing.Queue, stop: threading.Event) -> None:
        """Process task."""
        while True:
            if stop.is_set():
                break
            try:
                task = task_queue.get(timeout=MetricsWorker.QUEUE_TIMEOUT)
            except queue.Empty:
                time.sleep(60)
            else:
                try:
                    MetricsWorker.process_task(metrics_client, task)
                    time.sleep(0.1)
                except Exception as exc:  # pylint: disable=[broad-except]
                    logger.exception(exc)

    @staticmethod
    def process_task(metrics_client: "BaseMetricsService", task: Task) -> None:
        """Process."""
        try:
            func = getattr(metrics_client, task.func_name)
            func(*task.args, **task.kwargs)
        except AttributeError:
            logger.error(f"Got unknown metrics method: {task.func_name}")
        except Exception as exc:
            logger.error(f"Exception while processing metrics: {exc}")


class MetricsExecutor:
    """ Exports metrics from queue """

    QUEUE_TIMEOUT = 3

    def __init__(self, metrics_client: "BaseMetricsService", task_queue: multiprocessing.Queue):
        self.task_queue = task_queue
        self.stop = threading.Event()
        self.metrics_client = metrics_client
        self.tasks_manager = threading.Thread(
            target=MetricsWorker.run,
            name="Metrics Executor Thread",
            kwargs={
                "metrics_client": self.metrics_client,
                "task_queue": self.task_queue,
                "stop": self.stop,
            },
            daemon=True,
        )

    def run(self) -> None:
        """Run tasks."""
        self.tasks_manager.start()

    @classmethod
    def add_task_to_queue(cls, _queue: multiprocessing.Queue, func_name: str, *args: Any, **kwargs: Any) -> None:
        task = Task(func_name=func_name, args=args, kwargs=kwargs)
        _queue.put_nowait(task)

    def close(self) -> None:
        """Close."""
        self.stop.set()
