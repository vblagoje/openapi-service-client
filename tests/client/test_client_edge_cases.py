import pytest

from openapi_service_client import OpenAPIServiceClient
from tests.conftest import FastAPITestClient


class TestEdgeCases:
    def test_invalid_openapi_spec(self):
        with pytest.raises(ValueError, match="Invalid OpenAPI specification format"):
            OpenAPIServiceClient("invalid_spec.yml")

    def test_missing_operation_id(self, test_files_path):
        client = OpenAPIServiceClient(
            test_files_path / "openapi_edge_cases.yml",
            FastAPITestClient(None),
        )

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
