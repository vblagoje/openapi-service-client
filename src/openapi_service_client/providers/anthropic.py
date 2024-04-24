from openapi_service_client.providers.llm_provider import LLMProvider, OpenAPISpecificationConverter
from openapi_service_client.providers.openai import OpenAIConverter
from openapi_service_client.providers.payload_extractor import DefaultPayloadExtractor, FunctionPayloadExtractor
from openapi_service_client.spec import OpenAPISpecification


class AnthropicLLMProvider(LLMProvider):

    def get_payload_extractor(self) -> FunctionPayloadExtractor:
        # See how Anthropic LLM function payloads are structured at https://docs.anthropic.com/claude/docs/tool-use
        return DefaultPayloadExtractor(arguments_field_name="input")

    def get_schema_converter(self, openapi_spec: OpenAPISpecification) -> OpenAPISpecificationConverter:
        # anthropic is using the same conversion format as OpenAI except for the parameters name
        # See https://docs.anthropic.com/claude/docs/tool-use for more information on function definition format.
        return OpenAIConverter(schema=openapi_spec, parameters_name="input_schema")
