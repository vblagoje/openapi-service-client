from typing import Any, Dict, List, Protocol


class OpenAPISpecificationConverter(Protocol):

    def convert(self) -> List[Dict[str, Any]]:
        """
        Converts an OpenAPI specification into a list of LLM specific function definitions.
        :return: a list of function definitions represented as dictionaries.
        """
        pass
