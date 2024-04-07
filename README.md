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
To use the `OpenAPIServiceClient`, you need to have an OpenAPI specification file (in YAML or JSON format) that describes the API you want to interact with. Below are examples of how to use the library with both explicit and implicit authentication configurations.

### Explicit Authentication
In this example, we explicitly define the authentication mechanism by using ApiKeyAuthentication to provide the API key.

```python
from openapi_service_client import OpenAPIServiceClient
from openapi_service_client.config import ApiKeyAuthentication

api = OpenAPIServiceClient(
    openapi_spec="/path/to/weather_service.yml",
    auth_config=ApiKeyAuthentication(api_key="your_api_key")
)

payload = {
    "type": "function",
    "name": "weather_forecast",
    "arguments": {
        "location": "San Francisco, CA",
        "num_days": 3
    }
}

response = api.invoke(payload)
print(response)
```

In this scenario, ApiKeyAuthentication is utilized to directly provide the API key as part of the authentication configuration. You might want to use this approach when you want to explicitly specify the authentication method and provide the necessary credentials.

### Implicit Authentication
Alternatively, you can pass your secret token directly, and `OpenAPIServiceClient` will deduce the appropriate authentication method based on the OpenAPI specification. This approach is useful when you want the library to automatically select the correct authentication strategy.

```python

from openapi_service_client import OpenAPIServiceClient

api = OpenAPIServiceClient(
    openapi_spec="/path/to/weather_service.yml",
    auth_config="your_secret_token"
)

payload = {
    "type": "function",
    "name": "weather_forecast",
    "arguments": {
        "location": "San Francisco, CA",
        "num_days": 3
    }
}

response = api.invoke(payload)
print(response)
```
In this example, by providing a secret token as a string to auth_config, the library examines the OpenAPI specification to identify and apply the necessary authentication method (e.g., API key, OAuth2 token). This flexibility allows for a more straightforward setup when the authentication strategy can be inferred from the OpenAPI spec and the provided token.

## How It Works
`OpenAPIServiceClient` simplifies the process of invoking REST services defined by OpenAPI specifications. It takes care of the complexities involved in making HTTP requests, handling authentication, and processing responses.

When you provide an OpenAPI specification file to the client, it parses the specification and sets up the necessary request payloads and configurations to interact with the API based on the provided specification. You can then invoke specific operations using the OpenAI function-calling JSON format, which specifies the operation name and its arguments.

The client handles the REST invocation by constructing the appropriate HTTP request based on the OpenAPI specification. It takes care of parameter placing (path, query, requestBody etc.), payload formatting, authentication, and error handling. The response from the API is then returned to the caller for further processing.

By leveraging the OpenAPI specification, `OpenAPIServiceClient` eliminates the need for manual request setup and simplifies the integration process. It allows you to focus on working with LLM-generated function calls and seamlessly invoke the underlying services.
## Configuration

OpenAPI Service Client provides various configuration options to customize the behavior of the client. You can configure authentication, HTTP client settings, and more. Refer to the documentation for detailed information on the available configuration options.

## Contributing

Contributions to OpenAPI Service Client are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

OpenAPI Service Client is open-source software licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more information.
