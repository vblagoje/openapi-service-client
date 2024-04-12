import os

import anthropic
import pytest

from openapi_service_client.client import OpenAPIServiceClient
from openapi_service_client.client_configuration import ClientConfigurationBuilder
from openapi_service_client.config import AnthropicPayloadExtractor
from openapi_service_client.schema_converter import AnthropicSchemaConverter


class TestClientLiveAnthropic:

    @pytest.mark.skipif("SERPERDEV_API_KEY" not in os.environ, reason="SERPERDEV_API_KEY not set")
    @pytest.mark.skipif("ANTHROPIC_API_KEY" not in os.environ, reason="ANTHROPIC_API_KEY not set")
    def test_serperdev(self, test_files_path):
        builder = ClientConfigurationBuilder()
        config = (
            builder.with_openapi_spec(test_files_path / "serper.yaml")
            .with_credentials(os.getenv("SERPERDEV_API_KEY"))
            .with_provider(AnthropicPayloadExtractor())
            .build()
        )
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        converter = AnthropicSchemaConverter()
        tool_choice = converter.convert(config.get_openapi_spec())
        response = client.beta.tools.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=1024,
            tools=[tool_choice[0]],
            messages=[{"role": "user", "content": "Do a google search: Who was Nikola Tesla?"}],
        )
        tool_payload = response.content[1].to_dict()
        serper_api = OpenAPIServiceClient(config)
        response = serper_api.invoke(tool_payload)
        assert "inventions" in str(response)

    @pytest.mark.skipif("ANTHROPIC_API_KEY" not in os.environ, reason="ANTHROPIC_API_KEY not set")
    def test_github(self, test_files_path):
        builder = ClientConfigurationBuilder()
        config = (
            builder.with_openapi_spec(test_files_path / "github_compare.yml")
            .with_provider(AnthropicPayloadExtractor())
            .build()
        )

        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

        converter = AnthropicSchemaConverter()
        tool_choice = converter.convert(config.get_openapi_spec())
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
        tool_payload = response.content[1].to_dict()
        serper_api = OpenAPIServiceClient(config)
        response = serper_api.invoke(tool_payload)
        assert "deepset" in str(response)
