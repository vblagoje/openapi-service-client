import os

import cohere
import pytest

from openapi_service_client.client import OpenAPIServiceClient
from openapi_service_client.client_configuration import ClientConfigurationBuilder
from openapi_service_client.providers import CohereLLMProvider

# Copied from Cohere's documentation
preamble = """
## Task & Context
You help people answer their questions and other requests interactively. You will be asked a very wide array of
 requests on all kinds of topics. You will be equipped with a wide range of search engines or similar tools to
 help you, which you use to research your answer. You should focus on serving the user's needs as best you can,
 which will be wide-ranging.

## Style Guide
Unless the user asks for a different style of answer, you should answer in full sentences, using proper grammar and
 spelling.
"""


class TestClientLiveCohere:

    @pytest.mark.skipif("SERPERDEV_API_KEY" not in os.environ, reason="SERPERDEV_API_KEY not set")
    @pytest.mark.skipif("COHERE_API_KEY" not in os.environ, reason="COHERE_API_KEY not set")
    def test_serperdev(self, test_files_path):
        builder = ClientConfigurationBuilder()
        config = (
            builder.with_openapi_spec(test_files_path / "serper.yaml")
            .with_credentials(os.getenv("SERPERDEV_API_KEY"))
            .with_provider(CohereLLMProvider())
            .build()
        )
        client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))

        tool_choices = config.get_tools_definitions()
        response = client.chat(
            model="command-r",
            preamble=preamble,
            tools=tool_choices,
            message="Do a google search: Who was Nikola Tesla?",
        )
        tool_payload = response.tool_calls[0].dict()
        serper_api = OpenAPIServiceClient(config)
        response = serper_api.invoke(tool_payload)
        assert "inventions" in str(response)

    @pytest.mark.skipif("COHERE_API_KEY" not in os.environ, reason="COHERE_API_KEY not set")
    def test_github(self, test_files_path):
        builder = ClientConfigurationBuilder()
        config = (
            builder.with_openapi_spec(test_files_path / "github_compare.yml").with_provider(CohereLLMProvider()).build()
        )

        client = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
        tool_choices = config.get_tools_definitions()
        response = client.chat(
            model="command-r",
            preamble=preamble,
            tools=tool_choices,
            message="Compare branches main and add_default_adapter_filters in repo haystack and owner deepset-ai",
        )
        tool_payload = response.tool_calls[0].dict()
        serper_api = OpenAPIServiceClient(config)
        response = serper_api.invoke(tool_payload)
        assert "deepset" in str(response)
