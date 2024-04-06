from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import requests

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


class AbstractHttpClient(ABC):
    @abstractmethod
    def send_request(self, request: Dict[str, Any]) -> Any:
        pass


class RequestsHttpClient(AbstractHttpClient):
    def __init__(self, config: Optional[HttpClientConfig] = None):
        self.config = config or HttpClientConfig()
        self.session = requests.Session()
        self._initialize_session()

    def _initialize_session(self) -> None:
        self.session.headers.update(self.config.default_headers)
        # set session configurations based on the HttpClientConfig

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
            # Handle HTTP errors
            raise HttpClientError(f"HTTP error occurred: {e}") from e
        except requests.exceptions.RequestException as e:
            # Handle other request exceptions
            raise HttpClientError(f"HTTP error occurred: {e}") from e


class HttpClientError(Exception):
    pass
