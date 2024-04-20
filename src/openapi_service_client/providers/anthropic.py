import logging

from openapi_service_client.providers.llm_provider import LLMProvider, OpenAPISpecificationConverter
from openapi_service_client.providers.openai import OpenAISchemaConverter
from openapi_service_client.providers.payload_extractor import FunctionPayloadExtractor, GenericPayloadExtractor
from openapi_service_client.spec import OpenAPISpecification

MIN_REQUIRED_OPENAPI_SPEC_VERSION = 3

logger = logging.getLogger(__name__)


class AnthropicLLMProvider(LLMProvider):

    def get_payload_extractor(self) -> FunctionPayloadExtractor:
        # See https://docs.anthropic.com/claude/docs/tool-use for more information.
        return GenericPayloadExtractor(arguments_field_name="input")

    def get_schema_converter(self, openapi_spec: OpenAPISpecification) -> OpenAPISpecificationConverter:
        # anthropic is using the same conversion format as OpenAI except for the parameters name
        return OpenAISchemaConverter(schema=openapi_spec, parameters_name="input_schema")
