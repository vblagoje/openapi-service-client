from typing import Any

from openapi_service_client.client_configuration import ClientConfiguration
from openapi_service_client.request_builder import RequestBuilder


class OpenAPIServiceClient:
    """
    A client for invoking operations on REST services defined by OpenAPI specifications.

    Together with the `ClientConfiguration`, its `ClientConfigurationBuilder`, the `OpenAPIServiceClient`
    simplifies the process of integrating Large Language Models (LLMs) with services defined by OpenAPI specifications.

    The client abstracts away the complexities of making HTTP requests, handling authentication,
    preparing invocation payloads, and processing responses. It allows users to easily invoke
    operations on the target API using LLM-generated function calls.

    The `OpenAPIServiceClient` works with several LLM providers, including OpenAI, Anthropic, and Cohere.
    It uses a common method, `config.get_tools_definitions()`, to abstract each provider's unique way
    of defining functions. Similarly, differences in how these providers output function calls are
    handled uniformly through the `LLMProvider` and its `FunctionPayloadExtractor`.

    To invoke an operation, you can simply pass the LLM-generated function-calling payload to the
    `invoke` method of the `OpenAPIServiceClient`. The client automatically extracts and processes the
    payload, regardless of the LLM source, offering a truly plug-and-play experience.

    Example usage with OpenAI LLM provider and https://serper.dev/ search service:


    ```python
    import os
    from openai import OpenAI
    from openapi_service_client.client import OpenAPIServiceClient
    from openapi_service_client.client_configuration import ClientConfigurationBuilder

    # Configure the API client
    builder = ClientConfigurationBuilder()
    config = (
        builder.with_openapi_spec("https://bit.ly/serper_dev_spec_yaml")
        .with_credentials(os.getenv("SERPERDEV_API_KEY"))
        .build()
    )

    # Setup the OpenAI API client...
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # and send the chat message to create a function-calling response completion
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": "Do a google search: Who was Nikola Tesla?"}],
        tools=config.get_tools_definitions()
    )

    # Initialize the OpenAPIServiceClient with configuration
    serper_api = OpenAPIServiceClient(config)

    # Simply pass the LLM response and invoke the service
    # The LLM specific function-calling payload is extracted and processed automatically
    service_response = serper_api.invoke(response)
    print(service_response)
    ```
    """

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
