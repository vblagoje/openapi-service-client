import os

import anthropic
import pytest

from openapi_service_client.client import OpenAPIServiceClient
from openapi_service_client.client_configuration import ClientConfigurationBuilder
from openapi_service_client.providers import AnthropicLLMProvider


class TestClientLiveAnthropic:

    @pytest.mark.skipif("SERPERDEV_API_KEY" not in os.environ, reason="SERPERDEV_API_KEY not set")
    @pytest.mark.skipif("ANTHROPIC_API_KEY" not in os.environ, reason="ANTHROPIC_API_KEY not set")
    def test_serperdev(self):
        builder = ClientConfigurationBuilder()
        config = (
            builder.with_openapi_spec("https://bit.ly/serper_dev_spec_yaml")
            .with_credentials(os.getenv("SERPERDEV_API_KEY"))
            .with_provider(AnthropicLLMProvider())
            .build()
        )
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        tool_choice = config.get_tools_definitions()
        response = client.beta.tools.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            tools=[tool_choice[0]],
            messages=[{"role": "user", "content": "Do a google search: Who was Nikola Tesla?"}],
        )
        service_api = OpenAPIServiceClient(config)
        service_response = service_api.invoke(response)
        assert "inventions" in str(service_response)

        # make a few more requests to test the same tool
        service_response = service_api.invoke(response)
        assert "Serbian" in str(service_response)

        service_response = service_api.invoke(response)
        assert "American" in str(service_response)

    @pytest.mark.skipif("ANTHROPIC_API_KEY" not in os.environ, reason="ANTHROPIC_API_KEY not set")
    def test_github(self, test_files_path):
        builder = ClientConfigurationBuilder()
        config = (
            builder.with_openapi_spec(test_files_path / "github_compare.yml")
            .with_provider(AnthropicLLMProvider())
            .build()
        )

        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        tool_choice = config.get_tools_definitions()
        response = client.beta.tools.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            tools=[tool_choice[0]],
            messages=[
                {
                    "role": "user",
                    "content": "Compare branches main and add_default_adapter_filters in repo"
                    " haystack and owner deepset-ai",
                }
            ],
        )
        service_api = OpenAPIServiceClient(config)
        service_response = service_api.invoke(response)
        assert "deepset" in str(service_response)
