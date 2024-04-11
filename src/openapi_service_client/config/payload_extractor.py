import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List


class FunctionPayloadExtractor(ABC):

    @abstractmethod
    def extract_function_invocation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
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

    def search(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(payload, dict):
            if all(field in payload for field in self.required_fields()):
                return payload
            for _, value in payload.items():
                if isinstance(value, dict):
                    result = self.search(value)
                    if result:
                        return result

        elif isinstance(payload, list):
            for item in payload:
                result = self.search(item)
                if result:
                    return result
        return {}


class OpenAIPayloadExtractor(FunctionPayloadExtractor):
    def extract_function_invocation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        fields_and_values = self.search(payload)
        if fields_and_values:
            args = fields_and_values.get("arguments")
            if not isinstance(args, (str, dict)):
                raise ValueError(f"Invalid arguments type {type(args)} for OpenAI function call, expected str or dict")
            return {
                "name": fields_and_values.get("name"),
                "arguments": json.loads(args) if isinstance(args, str) else args,
            }
        return {}

    def required_fields(self) -> List[str]:
        return ["name", "arguments"]


class AnthropicPayloadExtractor(FunctionPayloadExtractor):
    def extract_function_invocation(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        fields_and_values = self.search(payload)
        if fields_and_values:
            arguments = fields_and_values.get("input")
            if not isinstance(arguments, dict):
                raise ValueError(f"Invalid input type {type(arguments)} for Anthropic function call, expected dict")
            return {"name": fields_and_values.get("name"), "arguments": arguments}
        return {}

    def required_fields(self) -> List[str]:
        return ["name", "input"]
