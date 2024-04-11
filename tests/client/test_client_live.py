import json
import os

import pytest

from openapi_service_client.client import OpenAPIServiceClient
from openapi_service_client.client_configuration import ClientConfigurationBuilder


class TestClientLive:

    @pytest.mark.skipif("SERPERDEV_API_KEY" not in os.environ, reason="SERPERDEV_API_KEY not set")
    def test_serperdev(self, test_files_path):
        builder = ClientConfigurationBuilder()
        config = (
            builder.with_openapi_spec(test_files_path / "serper.yaml")
            .with_credentials(os.getenv("SERPERDEV_API_KEY"))
            .build()
        )
        serper_api = OpenAPIServiceClient(config)
        payload = {
            "id": "call_NJr1NBz2Th7iUWJpRIJZoJIA",
            "function": {
                "arguments": '{"q": "Who was Zoran Djindjic?"}',
                "name": "serperdev_search",
            },
            "type": "function",
        }
        response = serper_api.invoke(payload)
        assert "politician" in str(response)

    def test_github(self, test_files_path):
        builder = ClientConfigurationBuilder()
        config = builder.with_openapi_spec(test_files_path / "github_compare.yml").build()
        api = OpenAPIServiceClient(config)

        params = {"owner": "deepset-ai", "repo": "haystack", "basehead": "main...add_default_adapter_filters"}
        payload = {
            "id": "call_NJr1NBz2Th7iUWJpRIJZoJIA",
            "function": {
                "arguments": json.dumps(params),
                "name": "compare",
            },
            "type": "function",
        }
        response = api.invoke(payload)
        assert "deepset" in str(response)
