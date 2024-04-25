import logging
from typing import Any, Dict, Optional, Protocol

import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from openapi_service_client.config.configuration import HttpClientConfig

VALID_HTTP_METHODS = [
    "get",
    "put",
    "post",
    "delete",
    "options",
    "head",
    "patch",
    "trace",
]

logger = logging.getLogger(__name__)


class HttpClient(Protocol):
    def send_request(self, request: Dict[str, Any]) -> Any:
        """
        Send an HTTP request and return the response.
        :param request: a dictionary containing the request details.
        :return: the response from the HTTP request.
        """
        pass


class RequestsHttpClient(HttpClient):
    def __init__(self, config: Optional[HttpClientConfig] = None):
        self.config = config or HttpClientConfig()
        self.session = requests.Session()
        self._initialize_session()

    def _initialize_session(self) -> None:
        retries = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.backoff_factor,
            status_forcelist=self.config.retry_on_status,
        )
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        self.session.headers.update(self.config.default_headers)

    def send_request(self, request: Dict[str, Any]) -> Any:
        url = request["url"]
        method = request["method"]
        headers = {**self.config.default_headers, **request.get("headers", {})}
        params = request.get("params", {})
        json_data = request.get("json", None)
        auth = request.get("auth", None)
        try:
            response = self.session.request(method, url, headers=headers, params=params, json=json_data, auth=auth)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.warning(f"HTTP error occurred: {e} while sending request to {url}")
            raise HttpClientError(f"HTTP error occurred: {e}") from e
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error occurred: {e} while sending request to {url}")
            raise HttpClientError(f"HTTP error occurred: {e}") from e
        except Exception as e:
            logger.warning(f"An error occurred: {e} while sending request to {url}")
            raise HttpClientError(f"An error occurred: {e}") from e


class HttpClientError(Exception):
    pass
