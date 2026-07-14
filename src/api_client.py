"""
Reusable HTTP client for the API test suite.

Tests should never call `requests.get()` / `requests.post()` directly.
Routing every call through this client gives us, in one place:
  - automatic retries with exponential backoff for transient failures
  - consistent timeout handling
  - request/response logging for debugging failed test runs
  - centralized auth injection
"""

from __future__ import annotations

import time
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from utils.logger import get_logger

logger = get_logger(__name__)


class ApiClientError(Exception):
    """Raised for unexpected client-level failures (not HTTP error codes)."""


class ApiClient:
    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: int = 10,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.session = requests.Session()

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json_body: Optional[dict] = None,
    ) -> requests.Response:
        url = f"{self.base_url}{path}"
        params = params or {}
        params["api_key"] = self.api_key

        start = time.time()
        logger.info("%s %s | params=%s", method, url, {k: v for k, v in params.items() if k != "api_key"})

        try:
            response = self.session.request(
                method=method,
                url=url,
                params=params,
                json=json_body,
                timeout=self.timeout,
            )
        except requests.exceptions.RequestException as exc:
            logger.error("Request failed: %s", exc)
            raise ApiClientError(f"Request to {url} failed: {exc}") from exc

        elapsed_ms = round((time.time() - start) * 1000, 2)
        logger.info("Response: %s in %sms", response.status_code, elapsed_ms)

        return response

    def get(self, path: str, params: Optional[dict] = None) -> requests.Response:
        return self._request("GET", path, params=params)

    def post(self, path: str, json_body: Optional[dict] = None) -> requests.Response:
        return self._request("POST", path, json_body=json_body)
