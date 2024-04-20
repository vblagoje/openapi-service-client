import dataclasses
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class FunctionPayloadExtractor(ABC):

    @abstractmethod
    def extract_function_invocation(self, payload: Any) -> Dict[str, Any]:
        """
        Extracts the function name and arguments from the LLM generated function call payload.

        Regardless of the LLM provider the return value should be a dictionary containing the function name
        and arguments under the keys "name" and "arguments" respectively. If payload is not found, an empty
        dictionary should be returned.

        :param payload: The LLM generated function call payload.
        :returns: A dictionary containing the function name and arguments.
                - `name`: The name of the function to be called.
                - `arguments`: The arguments to be passed to the function.
        """
        pass

    @abstractmethod
    def required_fields(self) -> List[str]:
        """
        Returns a list of required fields that must be present in the function call payload.
        :returns: A list of required fields to find in the function call payload.
        """
        pass

    def search(self, payload: Any) -> Dict[str, Any]:
        if self.is_pydantic(payload):
            payload = payload.dict()
        elif dataclasses.is_dataclass(payload):
            payload = dataclasses.asdict(payload)

        if isinstance(payload, dict):
            if all(field in payload for field in self.required_fields()):
                return payload
            for _, value in payload.items():
                result = self.search(value)
                if result:
                    return result

        elif isinstance(payload, list):
            for item in payload:
                result = self.search(item)
                if result:
                    return result

        return {}

    def is_pydantic(self, obj: Any) -> bool:
        # pydantic v1 and v2 models have a dict method that can be used to convert the model to a dictionary
        return hasattr(obj, "dict") and callable(obj.dict)


class GenericPayloadExtractor(FunctionPayloadExtractor):
    def __init__(self, arguments_field_name: str):
        self.arguments_field_name = arguments_field_name

    def extract_function_invocation(self, payload: Any) -> Dict[str, Any]:
        fields_and_values = self.search(payload)
        if fields_and_values:
            arguments = fields_and_values.get(self.arguments_field_name)
            if not isinstance(arguments, dict):
                raise ValueError(
                    f"Invalid {self.arguments_field_name} type {type(arguments)} for function call, expected dict"
                )
            return {"name": fields_and_values.get("name"), "arguments": arguments}
        return {}

    def required_fields(self) -> List[str]:
        return ["name", self.arguments_field_name]
