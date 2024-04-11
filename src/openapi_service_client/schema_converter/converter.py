from typing import Any, Dict, List, Protocol

from openapi_service_client.spec import OpenAPISpecification


class OpenAPISpecificationConverter(Protocol):

    def convert(self, spec: OpenAPISpecification) -> List[Dict[str, Any]]:
        """
        Converts an OpenAPI specification into a list of function definitions.

        :param spec: The OpenAPI specification to convert.
        :return: a list of function definitions represented as dictionaries.
        """
        pass
