# OpenAPI Service Client
[![PyPI - Version](https://img.shields.io/pypi/v/openapi-service-client.svg)](https://pypi.org/project/openapi-service-client)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/openapi-service-client.svg)](https://pypi.org/project/openapi-service-client)


OpenAPI Service Client is a Python library that enables effortless integration between Large Language Models (LLMs) and services defined by OpenAPI specifications. It provides a simple and intuitive way to invoke REST services using the function-calling JSON format, making it easy to integrate with LLM-generated function calls.

## Motivation

The OpenAPI Service Client library aims to simplify the process of invoking OpenAPI-defined services using function-calling payloads from various LLM providers. By abstracting away the complexities of making HTTP requests, handling authentication, preparing invocation payloads, and processing responses, it allows users to easily invoke underlying services with LLM-generated function calls.

The library supports multiple LLM providers, including OpenAI, Anthropic, and Cohere. Each LLM provider uses a unique function-calling schema definition format; OpenAPI Service Client abstracts these differences, enabling a uniform approach to service invocation. Additionally, the library provides a flexible and extensible architecture that allows users to add support for additional LLM providers and function-calling formats.

## Features

- Easy integration with LLM-generated function calls
- Support for various LLM providers, including OpenAI, Anthropic, and Cohere
- Automatic handling of REST invocations based on OpenAPI specifications
- Support for various authentication strategies, including API key, HTTP authentication, and OAuth2
- Flexible configuration options for adapting the client behavior
- Extensible architecture for adding support for additional LLM providers and function-calling formats


## Installation

You can install OpenAPI Service Client using pip:

```shell
pip install openapi-service-client
```

## Usage

To use `OpenAPIServiceClient`, follow these steps to configure and invoke operations on your target API (aka tool/service) defined by an OpenAPI specification.

### OpenAI Example

To run the OpenAI example below, you need:
1) Install openai package (`pip install openai`)
2) OpenAI API key. You can obtain an OpenAI API key by signing up for an account on the OpenAI platform. See https://platform.openai.com/ for more details.
3) SerperDev API key. This api key is required to access the SerperDev Google search engine API. See https://serper.dev/ for a quick signup and free credits. 


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

# Initialize the OpenAPIServiceClient with configuration
serper_api = OpenAPIServiceClient(config)

# Setup the OpenAI API client and send the chat message
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tool_choice = config.get_tools_definitions()
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Do a google search: Who was Nikola Tesla?"}],
    tools=[{"type": "function", "function": tool_choice[0]}],
    tool_choice={"type": "function", "function": {"name": tool_choice[0]["name"]}},
)

# Extract the function-calling payload from response and invoke the service
tool_payloads = response.choices[0].message.tool_calls
response = serper_api.invoke(tool_payloads[0].to_dict())
print(response)
```

### Anthropic Example

To run the Anthropic Claude Opus example below, you need:

1) Install anthropic package (`pip install anthropic`)
2) Anthropic API key. You can obtain an Anthropic API key by signing up for an account on the Anthropic platform. See https://www.anthropic.com/ for more details.
3) SerperDev API key. This api key is required to access the SerperDev Google search engine API. See https://serper.dev/ for a quick signup and free credits. 


```python
import os
import anthropic
from openapi_service_client.client import OpenAPIServiceClient
from openapi_service_client.client_configuration import ClientConfigurationBuilder
from openapi_service_client.providers import AnthropicLLMProvider

# Configure the API client
builder = ClientConfigurationBuilder()
config = (
    builder.with_openapi_spec("https://bit.ly/serper_dev_spec_yaml")
    .with_credentials(os.getenv("SERPERDEV_API_KEY"))
    .with_provider(AnthropicLLMProvider())
    .build()
)

# Initialize the OpenAPIServiceClient with configuration
serper_api = OpenAPIServiceClient(config)

# Setup the Anthropic API client and send the chat message
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Create a message request using the Anthropic API client
response = client.beta.tools.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    tools=config.get_tools_definitions(),
    messages=[{"role": "user", "content": "Do a google search: Who was Nikola Tesla?"}],
)

# Extract the function-calling payload from the response and invoke the service
tool_payload = response.content[1].to_dict()
response = serper_api.invoke(tool_payload)
print(response)
```
### Cohere Example

To run the Cohere Command-R example below, you need:

1) Install cohere package (`pip install cohere`)
2) Cohere API key. You can obtain Cohere API key by signing up for an account on the Cohere platform. See https://cohere.ai/ for more details.
3) SerperDev API key. This api key is required to access the SerperDev Google search engine API. See https://serper.dev/ for a quick signup and free credits. 


```python
import os
import cohere
from openapi_service_client.client import OpenAPIServiceClient
from openapi_service_client.client_configuration import ClientConfigurationBuilder
from openapi_service_client.providers import CohereLLMProvider

# Configure the API client
builder = ClientConfigurationBuilder()
config = (
    builder.with_openapi_spec("https://bit.ly/serper_dev_spec_yaml")
    .with_credentials(os.getenv("SERPERDEV_API_KEY"))
    .with_provider(CohereLLMProvider())
    .build()
)

# Initialize the OpenAPIServiceClient with configuration
serper_api = OpenAPIServiceClient(config)

# Setup the Cohere client 
client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
tool_choices = config.get_tools_definitions()

# And send the chat message
response = client.chat(
    model="command-r",
    preamble="A preamble aka system prompt goes here.",
    tools=tool_choices,
    message="Do a google search: Who was Nikola Tesla?",
)

# Extract the function-calling payload and invoke the service
tool_payload = response.tool_calls[0].dict()
response = serper_api.invoke(tool_payload)
print(response)
```

## How It Works
`OpenAPIServiceClient` simplifies the process of invoking REST services defined by OpenAPI specifications. It takes care of the complexities involved in making HTTP requests, handling authentication, and processing responses.

When you provide an OpenAPI specification file to the client, it parses the specification and sets up the necessary request payloads and configurations to interact with the API based on the provided specification. You can then invoke specific operations using the OpenAI function-calling JSON format, which specifies the operation name and its arguments.

The client handles the REST invocation by constructing the appropriate HTTP request based on the OpenAPI specification. It takes care of parameter placing (path, query, requestBody etc.), payload formatting, authentication, and error handling. The response from the API is then returned to the caller for further processing.

By leveraging the OpenAPI specification, `OpenAPIServiceClient` eliminates the need for manual request setup and simplifies the integration process. It allows you to focus on working with LLM-generated function calls and seamlessly invoke the underlying services.

## Contributing

Contributions to OpenAPI Service Client are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

OpenAPI Service Client is open-source software licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more information.
