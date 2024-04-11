import logging

from openapi_service_client.schema_converter.openai import OpenAISchemaConverter

MIN_REQUIRED_OPENAPI_SPEC_VERSION = 3

logger = logging.getLogger(__name__)


class AnthropicSchemaConverter(OpenAISchemaConverter):
    def __init__(self):
        super().__init__(parameters_name="input_schema")
