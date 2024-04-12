from typing import Any, Dict

from openapi_service_client.client_configuration import ClientConfiguration
from openapi_service_client.http_client import VALID_HTTP_METHODS
from openapi_service_client.request_builder import RequestBuilder
from openapi_service_client.spec import Operation


class OpenAPIServiceClient:
    def __init__(
        self,
        client_config: ClientConfiguration,
    ):
        self.openapi_spec = client_config.get_openapi_spec()
        self.http_client = client_config.get_http_client()
        self.request_builder = RequestBuilder(client_config)
        self.provider = client_config.get_provider()

    def get_operations(self) -> Dict[str, Dict[str, Operation]]:
        operations: Dict[str, Dict[str, Operation]] = {}
        for path, path_item in self.openapi_spec.get_paths().items():
            operations[path] = {}
            for method, operation in path_item.items():
                if method in VALID_HTTP_METHODS:
                    operations[path][method] = operation
        return operations

    def invoke(self, function_payload: Dict[str, Any]) -> Any:
        payload_extractor = self.provider.get_payload_extractor()
        fn_invocation_payload = payload_extractor.extract_function_invocation(function_payload)
        if not fn_invocation_payload:
            raise OpenAPIClientError(
                f"Failed to extract function invocation payload from {function_payload} using "
                f"{payload_extractor.__class__.__name__}. Ensure the payload format matches the expected "
                "structure for the designated LLM extractor."
            )
        # fn_invocation_payload, if not empty, guaranteed to have "name" and "arguments" keys from here on
        operation = self.openapi_spec.find_operation_by_id(fn_invocation_payload.get("name"))
        request = self.request_builder.build_request(operation, **fn_invocation_payload.get("arguments"))
        return self.http_client.send_request(request)


class OpenAPIClientError(Exception):
    pass
