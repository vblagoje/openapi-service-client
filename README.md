# OpenAPI Service Client
[![PyPI - Version](https://img.shields.io/pypi/v/openapi-service-client.svg)](https://pypi.org/project/openapi-service-client)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/openapi-service-client.svg)](https://pypi.org/project/openapi-service-client)


OpenAPI Service Client is a Python library that enables seamless integration between Large Language Models (LLMs) and services defined by OpenAPI specifications. It provides a simple and intuitive way to invoke REST services using the OpenAI function-calling JSON format, making it easy to integrate with LLM-generated function calls.

## Features

- Seamless integration with LLM-generated function calls using OpenAI's function-calling JSON format
- Automatic handling of REST invocations and data retrieval based on OpenAPI specifications
- Support for various authentication strategies, including API key and HTTP authentication
- Flexible configuration options for adapting the client behavior
- Easy integration with existing Python projects

## Installation

You can install OpenAPI Service Client using pip:

```shell
pip install openapi-service-client
```

## Usage

To effectively use the `OpenAPIServiceClient`, follow these steps to configure and invoke operations on your target API defined by an OpenAPI specification.

### Step 1: Configuration

Begin by creating a client configuration using the `OpenAPIServiceClientConfigurationBuilder`. This configuration includes the path to your OpenAPI specification and the authentication details.

#### Configuration Example:

```python
from openapi_service_client import OpenAPIServiceClient
from openapi_service_client.client_configuration import OpenAPIServiceClientConfigurationBuilder

# Initialize the configuration builder
config_builder = OpenAPIServiceClientConfigurationBuilder()

# Build the configuration
config = (config_builder
          .with_openapi_spec("/path/to/your/openapi_spec.yaml")
          .with_credentials("your_api_key_or_bearer_token")
          .build())

# Create the client with the configured settings
api_client = OpenAPIServiceClient(config)
```

This example demonstrates a basic setup. You can further customize the configuration by specifying additional parameters such as a custom HTTP client or advanced authentication strategies.

### Step 2: Invoking API Operations
With the client configured, you can invoke operations defined in your OpenAPI specification. Simply pass OpenAI function-calling JSON payloads to the `invoke` method to call the desired operation.

```python
operation_payload = {
    "id": "call_UNIQUEID123456",
    "function": {
        "arguments": "{\"location\": \"San Francisco, CA\", \"num_days\": 3}",
        "name": "weather_forecast"
    },
    "type": "function"
}

# Execute the operation
response = api_client.invoke(operation_payload)
print(response)
```

In this example, operation_payload contains the necessary information to call the weather_forecast operation, specifying the city and the number of forecast days as arguments. The invoke method sends the request to the API and returns the response.

### Notes on Authentication

The `with_credentials` method in the configuration builder accommodates a variety of authentication mechanisms to suit different API security requirements:

- **API Key Authentication:** Use `ApiKeyAuthentication` when your API requires an API key. This class supports adding the API key in the request header, query parameters, or cookies, based on the API's specification.

    ```python
    from openapi_service_client.config import ApiKeyAuthentication
    config_builder.with_credentials(ApiKeyAuthentication(api_key="your_api_key"))
    ```

- **HTTP Authentication:** For APIs using HTTP Basic or Bearer Authentication, `HTTPAuthentication` allows you to specify credentials. Provide a username and password for Basic authentication, or a token for Bearer authentication.

    ```python
    from openapi_service_client.config import HTTPAuthentication

    # For Basic Auth
    config_builder.with_credentials(HTTPAuthentication(username="user", password="pass"))

    # For Bearer Token
    config_builder.with_credentials(HTTPAuthentication(token="your_bearer_token"))
    ```

- **OAuth2 Authentication:** Use `OAuthAuthentication` for APIs secured with OAuth2. Specify your access token and, if necessary, the token type (defaults to "Bearer").

    ```python
    from openapi_service_client.config import OAuthAuthentication

    config_builder.with_credentials(OAuthAuthentication(access_token="your_access_token", token_type="Bearer"))
    ```

Each authentication strategy is designed to integrate seamlessly with the OpenAPI specification's security schemes, ensuring your API calls are correctly authenticated according to the API's requirements.

#### Implicit Credentials

For a more straightforward setup, the `with_credentials` method allows passing a token directly as a string (or a dictionary), enabling implicit determination of the appropriate authentication strategy based on the API's security requirements.

```python
config_builder.with_credentials("your_bearer_token")
```

This method simplifies client configuration for APIs that accept a single token, automatically applying the correct authentication strategy without manual selection.


## How It Works
`OpenAPIServiceClient` simplifies the process of invoking REST services defined by OpenAPI specifications. It takes care of the complexities involved in making HTTP requests, handling authentication, and processing responses.

When you provide an OpenAPI specification file to the client, it parses the specification and sets up the necessary request payloads and configurations to interact with the API based on the provided specification. You can then invoke specific operations using the OpenAI function-calling JSON format, which specifies the operation name and its arguments.

The client handles the REST invocation by constructing the appropriate HTTP request based on the OpenAPI specification. It takes care of parameter placing (path, query, requestBody etc.), payload formatting, authentication, and error handling. The response from the API is then returned to the caller for further processing.

By leveraging the OpenAPI specification, `OpenAPIServiceClient` eliminates the need for manual request setup and simplifies the integration process. It allows you to focus on working with LLM-generated function calls and seamlessly invoke the underlying services.

## Contributing

Contributions to OpenAPI Service Client are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

OpenAPI Service Client is open-source software licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more information.
