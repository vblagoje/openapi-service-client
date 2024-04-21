import logging
from typing import Any, Callable, Dict, List, Optional

import jsonref

from openapi_service_client.providers.converter import OpenAPISpecificationConverter
from openapi_service_client.providers.llm_provider import LLMProvider
from openapi_service_client.providers.payload_extractor import (
    DefaultRecursivePayloadExtractor,
    FunctionPayloadExtractor,
)
from openapi_service_client.spec import OpenAPISpecification

MIN_REQUIRED_OPENAPI_SPEC_VERSION = 3

logger = logging.getLogger(__name__)


class OpenAILLMProvider(LLMProvider):

    def get_payload_extractor(self) -> FunctionPayloadExtractor:
        return DefaultRecursivePayloadExtractor(arguments_field_name="arguments")

    def get_schema_converter(self, openapi_spec: OpenAPISpecification) -> OpenAPISpecificationConverter:
        # each function in the OpenAI schema needs to be wrapped the below described json object
        return OpenAISchemaConverter(schema=openapi_spec, transform_fn=lambda fn: {"type": "function", "function": fn})


class OpenAISchemaConverter(OpenAPISpecificationConverter):

    def __init__(
        self,
        schema: OpenAPISpecification,
        parameters_name: str = "parameters",
        transform_fn: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None,
    ):
        self.schema = schema
        self.parameters_name = parameters_name
        self.transform_fn = transform_fn

    def convert(self) -> List[Dict[str, Any]]:
        resolved_schema = jsonref.replace_refs(self.schema.spec_dict)
        fn_definitions = self._openapi_to_functions(resolved_schema)
        return [self.transform_fn(fn) for fn in fn_definitions] if self.transform_fn else fn_definitions

    def _openapi_to_functions(self, service_openapi_spec: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extracts functions from the OpenAPI specification of the service and converts them into a format
        suitable for OpenAI function calling.

        :param service_openapi_spec: The OpenAPI specification from which functions are to be extracted.
        :type service_openapi_spec: Dict[str, Any]
        :return: A list of dictionaries, each representing a function. Each dictionary includes the function's
                 name, description, and a schema of its parameters.
        :rtype: List[Dict[str, Any]]
        """

        # Doesn't enforce rigid spec validation because that would require a lot of dependencies
        # We check the version and require minimal fields to be present, so we can extract functions
        spec_version = service_openapi_spec.get("openapi")
        if not spec_version:
            raise ValueError(f"Invalid OpenAPI spec provided. Could not extract version from {service_openapi_spec}")
        service_openapi_spec_version = int(spec_version.split(".")[0])

        # Compare the versions
        if service_openapi_spec_version < MIN_REQUIRED_OPENAPI_SPEC_VERSION:
            raise ValueError(
                f"Invalid OpenAPI spec version {service_openapi_spec_version}. Must be "
                f"at least {MIN_REQUIRED_OPENAPI_SPEC_VERSION}."
            )

        functions: List[Dict[str, Any]] = []
        for paths in service_openapi_spec["paths"].values():
            for path_spec in paths.values():
                function_dict = self._parse_endpoint_spec(path_spec)
                if function_dict:
                    functions.append(function_dict)
        return functions

    def _parse_endpoint_spec(self, resolved_spec: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not isinstance(resolved_spec, dict):
            logger.warning("Invalid OpenAPI spec format provided. Could not extract function.")
            return {}

        function_name = resolved_spec.get("operationId")
        description = resolved_spec.get("description") or resolved_spec.get("summary", "")

        schema: Dict[str, Any] = {"type": "object", "properties": {}}

        # requestBody section
        req_body_schema = (
            resolved_spec.get("requestBody", {}).get("content", {}).get("application/json", {}).get("schema", {})
        )
        if "properties" in req_body_schema:
            for prop_name, prop_schema in req_body_schema["properties"].items():
                schema["properties"][prop_name] = self._parse_property_attributes(prop_schema)

            if "required" in req_body_schema:
                schema.setdefault("required", []).extend(req_body_schema["required"])

        # parameters section
        for param in resolved_spec.get("parameters", []):
            if "schema" in param:
                schema_dict = self._parse_property_attributes(param["schema"])
                # these attributes are not in param[schema] level but on param level
                useful_attributes = ["description", "pattern", "enum"]
                schema_dict.update({key: param[key] for key in useful_attributes if param.get(key)})
                schema["properties"][param["name"]] = schema_dict
                if param.get("required", False):
                    schema.setdefault("required", []).append(param["name"])

        if function_name and description and schema["properties"]:
            return {"name": function_name, "description": description, self.parameters_name: schema}
        else:
            logger.warning(f"Invalid OpenAPI spec format provided. Could not extract function from {resolved_spec}")
            return {}

    def _parse_property_attributes(
        self, property_schema: Dict[str, Any], include_attributes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Recursively parses the attributes of a property schema, including nested objects and arrays,
        and includes specified attributes like description, pattern, etc.

        :param property_schema: The schema of the property to parse.
        :param include_attributes: The list of attributes to include in the parsed schema.
        :return: The parsed schema of the property including the specified attributes.
        """
        include_attributes = include_attributes or ["description", "pattern", "enum"]

        schema_type = property_schema.get("type")

        parsed_schema = {"type": schema_type} if schema_type else {}
        for attr in include_attributes:
            if attr in property_schema:
                parsed_schema[attr] = property_schema[attr]

        if schema_type == "object":
            properties = property_schema.get("properties", {})
            parsed_properties = {
                prop_name: self._parse_property_attributes(prop, include_attributes)
                for prop_name, prop in properties.items()
            }
            parsed_schema["properties"] = parsed_properties

            if "required" in property_schema:
                parsed_schema["required"] = property_schema["required"]

        elif schema_type == "array":
            items = property_schema.get("items", {})
            parsed_schema["items"] = self._parse_property_attributes(items, include_attributes)

        return parsed_schema
