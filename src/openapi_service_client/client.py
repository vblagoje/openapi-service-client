import json
from typing import Any, Dict

from openapi_service_client.client_configuration import OpenAPIServiceClientConfiguration
from openapi_service_client.http_client import VALID_HTTP_METHODS
from openapi_service_client.request_builder import RequestBuilder
from openapi_service_client.spec import Operation


class OpenAPIServiceClient:
    def __init__(
        self,
        client_config: OpenAPIServiceClientConfiguration,
    ):
        self.openapi_spec = client_config.get_openapi_spec()
        self.http_client = client_config.get_http_client()
        self.request_builder = RequestBuilder(client_config)

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
