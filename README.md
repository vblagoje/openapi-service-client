# OpenAPI Service Client
[![PyPI - Version](https://img.shields.io/pypi/v/openapi-service-client.svg)](https://pypi.org/project/openapi-service-client)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/openapi-service-client.svg)](https://pypi.org/project/openapi-service-client)


OpenAPI Service Client is a Python library that enables effortless integration between Large Language Models (LLMs) and services defined by OpenAPI specifications. It provides a simple and intuitive way to invoke REST services using the function-calling JSON format, making it easy to integrate with LLM-generated function calls.

## Motivation

The OpenAPI Service Client library aims to simplify the process of invoking OpenAPI-defined services using function-calling payloads from various LLM providers. By abstracting away the complexities of making HTTP requests, handling authentication, preparing invocation payloads, and processing responses, it allows users to easily invoke underlying services with LLM-generated function calls.

The library supports multiple LLM providers, including OpenAI, Anthropic, and Cohere. Each LLM provider uses a unique function-calling schema definition format; OpenAPI Service Client abstracts these differences, enabling a uniform approach to service invocation. Additionally, the library provides a flexible and extensible architecture that allows users to add support for additional LLM providers and function-calling formats.

## Features

- **Seamless LLM Integration**: Easily integrate with LLM-generated function calls for various providers, including OpenAI, Anthropic, and Cohere.
- **OpenAPI Compliance**: Automatically handle REST service invocations and support various authentication strategies (API key, HTTP authentication, OAuth2).
- **Customizable and Extensible**: Offers flexible configuration options and an extensible architecture to accommodate additional LLM providers and function-calling formats.

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

# Simply pass the LLM response and invoke the service
# The function-calling payload is extracted and processed automatically
service_response = serper_api.invoke(response)
print(service_response)
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

# Simply pass the LLM response and invoke the service
# The function-calling payload is extracted and processed automatically
service_response = serper_api.invoke(response)
print(service_response)
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

# And send the chat message
response = client.chat(
    model="command-r",
    preamble="A preamble aka system prompt goes here.",
    tools=config.get_tools_definitions(),
    message="Do a google search: Who was Nikola Tesla?",
)

# Simply pass the LLM response and invoke the service
# The function-calling payload is extracted and processed automatically
service_response = serper_api.invoke(response)
print(service_response)
```

## How It Works
`OpenAPIServiceClient` simplifies the process of invoking REST services defined by OpenAPI specifications. It takes care of the complexities involved in making HTTP requests, handling authentication, and processing responses.

When you provide an OpenAPI specification file to the client, it parses the specification and sets up the necessary request payloads and configurations to interact with the API based on the provided specification. You can then invoke specific operations using the OpenAI function-calling JSON format, which specifies the operation name and its arguments.

The client handles the REST invocation by constructing the appropriate HTTP request based on the OpenAPI specification. It takes care of parameter placing (path, query, requestBody etc.), payload formatting, authentication, and error handling. The response from the API is then returned to the caller for further processing.

By leveraging the OpenAPI specification, `OpenAPIServiceClient` eliminates the need for manual request setup and simplifies the integration process. It allows you to focus on working with LLM-generated function calls and seamlessly invoke the underlying services.

Note how in the examples above, the service invocation function in `OpenAPIServiceClient` directly accepts and processes function-calling payloads from various LLM providers. The client ensures that payloads are correctly identified and extracted, regardless of the LLM source, offering a truly plug-and-play experience.

## Contributing

Contributions to OpenAPI Service Client are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request on the GitHub repository.

## License

OpenAPI Service Client is open-source software licensed under the Apache License 2.0. See the [LICENSE](LICENSE) file for more information.
