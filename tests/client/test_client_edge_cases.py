import pytest

from openapi_service_client import OpenAPIServiceClient
from openapi_service_client.client_configuration import OpenAPIServiceClientConfigurationBuilder
from tests.conftest import FastAPITestClient


class TestEdgeCases:
    def test_invalid_openapi_spec(self):
        builder = OpenAPIServiceClientConfigurationBuilder()
        with pytest.raises(ValueError, match="Invalid OpenAPI specification format"):
            config = builder.with_openapi_spec("invalid_spec.yml").build()
            OpenAPIServiceClient(config)

    def test_missing_operation_id(self, test_files_path):
        builder = OpenAPIServiceClientConfigurationBuilder()
        config = (
            builder.with_openapi_spec(test_files_path / "openapi_edge_cases.yml")
            .with_http_client(FastAPITestClient(None))
            .build()
        )
        client = OpenAPIServiceClient(config)

        payload = {
            "type": "function",
            "function": {
                "arguments": '{"name": "John", "message": "Hola"}',
                "name": "missingOperationId",
            },
        }
        with pytest.raises(ValueError, match="No operation found with operationId"):
            client.invoke(payload)

    # TODO: Add more tests for edge cases
