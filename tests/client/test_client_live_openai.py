import os

import pytest
from openai import OpenAI

from openapi_service_client.client import OpenAPIServiceClient
from openapi_service_client.client_configuration import ClientConfigurationBuilder


class TestClientLiveOpenAPI:

    @pytest.mark.skipif("SERPERDEV_API_KEY" not in os.environ, reason="SERPERDEV_API_KEY not set")
    @pytest.mark.skipif("OPENAI_API_KEY" not in os.environ, reason="OPENAI_API_KEY not set")
    def test_serperdev(self, test_files_path):
        builder = ClientConfigurationBuilder()
        config = (
            builder.with_openapi_spec(test_files_path / "serper.yaml")
            .with_credentials(os.getenv("SERPERDEV_API_KEY"))
            .build()
        )
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        tool_choice = config.get_spec_converter().convert(config.get_openapi_spec())
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Do a google search: Who was Nikola Tesla?"}],
            tools=[{"type": "function", "function": tool_choice[0]}],
            tool_choice={"type": "function", "function": {"name": tool_choice[0]["name"]}},
        )
        tool_payloads = response.choices[0].message.tool_calls
        serper_api = OpenAPIServiceClient(config)
        response = serper_api.invoke(tool_payloads[0].to_dict())
        assert "inventions" in str(response)

    @pytest.mark.skipif("OPENAI_API_KEY" not in os.environ, reason="OPENAI_API_KEY not set")
    def test_github(self, test_files_path):
        builder = ClientConfigurationBuilder()
        config = builder.with_openapi_spec(test_files_path / "github_compare.yml").build()

        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        tool_choice = config.get_spec_converter().convert(config.get_openapi_spec())
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "user",
                    "content": "Compare branches main and add_default_adapter_filters in repo"
                    " haystack and owner deepset-ai",
                }
            ],
            tools=[{"type": "function", "function": tool_choice[0]}],
            tool_choice={"type": "function", "function": {"name": tool_choice[0]["name"]}},
        )
        tool_payloads = response.choices[0].message.tool_calls
        serper_api = OpenAPIServiceClient(config)
        response = serper_api.invoke(tool_payloads[0].to_dict())
        assert "deepset" in str(response)
