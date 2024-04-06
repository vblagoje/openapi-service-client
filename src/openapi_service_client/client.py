import json
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union

from src.openapi_service_client.config import AuthenticationStrategy
from src.openapi_service_client.http_client import (
    VALID_HTTP_METHODS,
    AbstractHttpClient,
    RequestsHttpClient,
)
from src.openapi_service_client.request_builder import RequestBuilder
from src.openapi_service_client.spec import OpenAPISpecification, Operation


class OpenAPIServiceClient:
    def __init__(
        self,
        openapi_spec: Union[str, Dict[str, Any]],
        http_client: Optional[AbstractHttpClient] = None,
        auth_config: Optional[AuthenticationStrategy] = None,
    ):
        if isinstance(openapi_spec, (str, Path)) and os.path.isfile(openapi_spec):
            self.openapi_spec = OpenAPISpecification.from_file(openapi_spec)
        elif isinstance(openapi_spec, dict):
            self.openapi_spec = OpenAPISpecification.from_dict(openapi_spec)
        else:
            raise ValueError("Invalid OpenAPI specification format. Expected file path or dictionary.")

        self.http_client = http_client or RequestsHttpClient()
        self.request_builder = RequestBuilder(self.openapi_spec, self.http_client, auth_config=auth_config)

    def get_operations(self) -> Dict[str, Dict[str, Operation]]:
        operations: Dict[str, Dict[str, Operation]] = {}
        for path, path_item in self.openapi_spec.get_paths().items():
            operations[path] = {}
            for method, operation in path_item.items():
                if method in VALID_HTTP_METHODS:
                    operations[path][method] = operation
        return operations

    def invoke(self, openai_fc_payload: Dict[str, Any]) -> Any:
        op_id: str = openai_fc_payload.get("function", {}).get("name", "")
        if not op_id:
            raise OpenAPIClientError(
                "Function name not provided in the function calling payload.",
                openai_fc_payload,
            )

        args_str = openai_fc_payload.get("function", {}).get("arguments", "")
        operation = self.openapi_spec.find_operation_by_id(op_id)
        request = self.request_builder.build_request(operation, **json.loads(args_str))
        return self.http_client.send_request(request)


class OpenAPIClientError(Exception):
    pass
