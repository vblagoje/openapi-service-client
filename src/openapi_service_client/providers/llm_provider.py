from typing import Protocol

from openapi_service_client.providers import FunctionPayloadExtractor, AnthropicPayloadExtractor, \
    CoherePayloadExtractor, OpenAIPayloadExtractor
from openapi_service_client.schema_converter import OpenAPISpecificationConverter, AnthropicSchemaConverter, \
    CohereSchemaConverter


class LLMProvider(Protocol):

    def get_payload_extractor(self) -> FunctionPayloadExtractor:
        pass

    def get_schema_converter(self) -> OpenAPISpecificationConverter:
        pass


class AnthropicLLMProvider(LLMProvider):

        def get_payload_extractor(self) -> FunctionPayloadExtractor:
            return AnthropicPayloadExtractor()

        def get_schema_converter(self) -> OpenAPISpecificationConverter:
            return AnthropicSchemaConverter()


class CohereLLMProvider(LLMProvider):

        def get_payload_extractor(self) -> FunctionPayloadExtractor:
            return CoherePayloadExtractor()

        def get_schema_converter(self) -> OpenAPISpecificationConverter:
            return CohereSchemaConverter()


class OpenAILLMProvider(LLMProvider):

        def get_payload_extractor(self) -> FunctionPayloadExtractor:
            return OpenAIPayloadExtractor()

        def get_schema_converter(self) -> OpenAPISpecificationConverter:
            return OpenAPISpecificationConverter()