from typing import Any

from openapi_service_client.client_configuration import ClientConfiguration
from openapi_service_client.request_builder import RequestBuilder


class OpenAPIServiceClient:
    def __init__(
        self,
        client_config: ClientConfiguration,
    ):
        self.openapi_spec = client_config.get_openapi_spec()
        self.http_client = client_config.get_http_client()
        self.request_builder = RequestBuilder(client_config)
        self.payload_extractor = client_config.get_payload_extractor()

    def invoke(self, function_payload: Any) -> Any:
        """
        Invokes a function specified in the function payload.

        Function payload is traversed to extract the function name and arguments, construct a request based on an
        OpenAPI specification, and send the request using a configured HTTP client.

        Function payload can be a dictionary, dataclass, or pydantic v1 and v2 model.

        :param function_payload: The function payload containing the details of the function to be invoked.
        :returns: The response from the service after invoking the function.
        :raises OpenAPIClientError: If the function invocation payload cannot be extracted from the function payload.
        :raises HttpClientError: If an error occurs while sending the request and receiving the response.
        """
        fn_invocation_payload = self.payload_extractor.extract_function_invocation(function_payload)
        if not fn_invocation_payload:
            raise OpenAPIClientError(
                f"Failed to extract function invocation payload from {function_payload} using "
                f"{self.payload_extractor.__class__.__name__}. Ensure the payload format matches the expected "
                "structure for the designated LLM extractor."
            )
        # fn_invocation_payload, if not empty, guaranteed to have "name" and "arguments" keys from here on
        operation = self.openapi_spec.find_operation_by_id(fn_invocation_payload.get("name"))
        request = self.request_builder.build_request(operation, **fn_invocation_payload.get("arguments"))
        return self.http_client.send_request(request)


class OpenAPIClientError(Exception):
    pass
