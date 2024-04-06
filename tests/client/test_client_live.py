import json
import os

import pytest

from openapi_service_client.client import OpenAPIServiceClient
from openapi_service_client.config.configuration import ApiKeyAuthentication


class TestClientLive:

    @pytest.mark.skipif("SERPERDEV_API_KEY" not in os.environ, reason="SERPERDEV_API_KEY not set")
    def test_serperdev(self, test_files_path):
        serper_api = OpenAPIServiceClient(
            openapi_spec=test_files_path / "serper.yaml",
            auth_config=ApiKeyAuthentication(api_key=os.getenv("SERPERDEV_API_KEY")),
        )
        payload = {
            "id": "call_NJr1NBz2Th7iUWJpRIJZoJIA",
            "function": {
                "arguments": '{"q": "Who was Zoran Djindjic?"}',
                "name": "search",
            },
            "type": "function",
        }
        response = serper_api.invoke(payload)
        assert "politician" in str(response)

    def test_github(self, test_files_path):
        api = OpenAPIServiceClient(
            openapi_spec=test_files_path / "github_compare.yml",
            auth_config=ApiKeyAuthentication("real_token_not_needed_here"),
        )

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
