import logging
from typing import Any, Dict, List

import jsonref

from openapi_service_client.providers.converter import OpenAPISpecificationConverter
from openapi_service_client.providers.llm_provider import LLMProvider
from openapi_service_client.providers.payload_extractor import FunctionPayloadExtractor, GenericPayloadExtractor
from openapi_service_client.spec import OpenAPISpecification

logger = logging.getLogger(__name__)


class CohereSchemaConverter(OpenAPISpecificationConverter):

    def __init__(self, schema: OpenAPISpecification):
        self.schema = schema

    def convert(self) -> List[Dict[str, Any]]:
        resolved_schema = jsonref.replace_refs(self.schema.spec_dict)
        return self._openapi_to_functions(resolved_schema)

    def _openapi_to_functions(self, service_openapi_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        functions = []
        for _, path_item in service_openapi_spec.get("paths", {}).items():
            for _, operation in path_item.items():
                function_dict = self._parse_endpoint(operation)
                if function_dict:
                    functions.append(function_dict)
        return functions

    def _parse_endpoint(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        function_name = operation.get("operationId")
        description = operation.get("description") or operation.get("summary", "")
        parameter_definitions = self._parse_parameters(operation)

        if function_name:
            return {
                "name": function_name,
                "description": description,
                "parameter_definitions": parameter_definitions,
            }
        else:
            logger.warning("Operation missing operationId, cannot create function definition.")
            return {}

    def _parse_parameters(self, operation: Dict[str, Any]) -> Dict[str, Any]:
        parameters = {}

        for param in operation.get("parameters", []):
            if "schema" in param:
                parameters[param["name"]] = self._parse_schema(
                    param["schema"], param.get("required", False), param.get("description", "")
                )

        if "requestBody" in operation:
            content = operation["requestBody"].get("content", {}).get("application/json", {})
            if "schema" in content:
                schema_properties = content["schema"].get("properties", {})
                required_properties = content["schema"].get("required", [])
                for name, schema in schema_properties.items():
                    parameters[name] = self._parse_schema(
                        schema, name in required_properties, schema.get("description", "")
                    )

        return parameters

    def _parse_schema(self, schema: Dict[str, Any], required: bool, description: str) -> Dict[str, Any]:  # noqa: FBT001
        schema_type = self._get_type(schema)
        if schema_type == "object":
            # Recursive call for complex types
            properties = schema.get("properties", {})
            nested_parameters = {
                name: self._parse_schema(
                    schema=prop_schema,
                    required=bool(name in schema.get("required", False)),
                    description=prop_schema.get("description", ""),
                )
                for name, prop_schema in properties.items()
            }
            return {
                "type": schema_type,
                "description": description,
                "properties": nested_parameters,
                "required": required,
            }
        else:
            return {"type": schema_type, "description": description, "required": required}

    def _get_type(self, schema: Dict[str, Any]) -> str:
        schema_type = schema.get("type", "object")
        if schema_type == "integer":
            return "int"
        elif schema_type == "string":
            return "str"
        elif schema_type == "boolean":
            return "bool"
        elif schema_type == "number":
            return "float"
        elif schema_type == "object":
            return "object"
        elif schema_type == "array":
            return "list"
        else:
            raise ValueError(f"Unsupported schema type {schema_type}")


class CohereLLMProvider(LLMProvider):

    def get_payload_extractor(self) -> FunctionPayloadExtractor:
        # See https://docs.cohere.com/docs/tool-use for more information.
        return GenericPayloadExtractor(arguments_field_name="parameters")

    def get_schema_converter(self, openapi_spec: OpenAPISpecification) -> OpenAPISpecificationConverter:
        return CohereSchemaConverter(schema=openapi_spec)
