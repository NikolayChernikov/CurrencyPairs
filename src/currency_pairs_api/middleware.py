"""Middleware module."""
# pylint: disable=broad-exception-caught
import logging
import re
import time
from typing import Callable, List, Optional

from fastapi import Request, Response
from starlette.routing import BaseRoute
from src.lib.monitoring import FastapiMetricsService

logger = logging.getLogger(__name__)


class MetricsMiddleware:
    """Metrics middleware."""

    def __init__(
            self,
            metrics_client: "FastapiMetricsService",
            routes: List[BaseRoute],
    ):
        self.metrics_client = metrics_client
        self.mapping = self.generate_routes_regex_mapping(routes=routes)

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # process the request and get the response
        start_time = time.time()
        response = await call_next(request)
        end_time = time.time()
        elapsed_time = end_time - start_time
        router_name = self.find_name_by_path(url_path=request.url.components.path)

        if request.url.components.path.find("/metrics") != -1:
            return response

        logger.debug(
            f"@METRICS@ processed request: {request.method=}, {request.url.components.path=}, "
            f"{response.status_code=}, {elapsed_time=:.2f}"
        )

        if not router_name:
            return response

        self.metrics_client.record_fastapi(endpoint_name=router_name, method=request.method,
                                           latency=elapsed_time, response_code=response.status_code)
        return response

    @classmethod
    def generate_routes_regex_mapping(cls, routes: List[BaseRoute]) -> dict:
        mapping = {}
        for route in routes:
            try:
                path = route.path  # type: ignore[attr-defined]
                path = re.sub(r'{[a-zA-Z0-9]*}', '[a-zA-Z0-9.]*', path)
                path += ".*"
                mapping[route.name] = re.compile(path)  # type: ignore[attr-defined]
                mapping.pop('get_health', None)
            except Exception:
                pass
        return mapping

    def find_name_by_path(self, url_path: str) -> Optional[str]:
        for name, re_compiled_path in self.mapping.items():
            if re.match(re_compiled_path, url_path):
                return name
        return None
