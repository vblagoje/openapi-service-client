from typing import Protocol

from openapi_service_client.providers.converter import OpenAPISpecificationConverter
from openapi_service_client.providers.payload_extractor import FunctionPayloadExtractor
from openapi_service_client.spec import OpenAPISpecification


class LLMProvider(Protocol):

    def get_payload_extractor(self) -> FunctionPayloadExtractor:
        pass

    def get_schema_converter(self, openapi_spec: OpenAPISpecification) -> OpenAPISpecificationConverter:
        pass
