import logging

from openapi_service_client.providers.llm_provider import LLMProvider, OpenAPISpecificationConverter
from openapi_service_client.providers.openai import OpenAISchemaConverter
from openapi_service_client.providers.payload_extractor import FunctionPayloadExtractor, GenericPayloadExtractor
from openapi_service_client.spec import OpenAPISpecification

MIN_REQUIRED_OPENAPI_SPEC_VERSION = 3

logger = logging.getLogger(__name__)


class AnthropicSchemaConverter(OpenAISchemaConverter):
    def __init__(self, schema: OpenAPISpecification):
        super().__init__(schema=schema, parameters_name="input_schema")


class AnthropicPayloadExtractor(GenericPayloadExtractor):
    """
    Extracts the function name and arguments from the Anthropic generated function call payload.
    See https://docs.anthropic.com/claude/docs/tool-use for more information.
    """

    def __init__(self):
        super().__init__(arguments_field_name="input")


class AnthropicLLMProvider(LLMProvider):

    def get_payload_extractor(self) -> FunctionPayloadExtractor:
        return AnthropicPayloadExtractor()

    def get_schema_converter(self, openapi_spec: OpenAPISpecification) -> OpenAPISpecificationConverter:
        return AnthropicSchemaConverter(schema=openapi_spec)
