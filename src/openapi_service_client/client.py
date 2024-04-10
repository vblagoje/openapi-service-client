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

    def _find_function_arguments(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(payload, dict):
            if "name" in payload and "arguments" in payload:
                return payload
            for _, value in payload.items():
                if isinstance(value, dict):
                    result = self._find_function_arguments(value)
                    if result:
                        return result
        raise OpenAPIClientError("No OpenAI function-calling JSON payload found", payload)

    def invoke(self, openai_fc_payload: Dict[str, Any]) -> Any:
        fn_invocation_payload = self._find_function_arguments(openai_fc_payload)

        # fn_invocation_payload guaranteed to have "name" and "arguments" keys from here on
        arguments = fn_invocation_payload.get("arguments")
        if isinstance(arguments, str):
            # it should always be a JSON string, but you never know with all LLM providers
            try:
                args = json.loads(arguments)
            except json.JSONDecodeError as e:
                raise OpenAPIClientError(f"Error parsing OpenAI function-calling arguments: {e!s}", arguments) from e
        elif isinstance(arguments, dict):
            args = arguments
        else:
            raise OpenAPIClientError(f"Invalid arguments type: {type(arguments)}", arguments)
        operation = self.openapi_spec.find_operation_by_id(fn_invocation_payload.get("name"))
        request = self.request_builder.build_request(operation, **args)
        return self.http_client.send_request(request)


class OpenAPIClientError(Exception):
    pass
