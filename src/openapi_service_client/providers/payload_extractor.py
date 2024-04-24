import dataclasses
import json
from typing import Any, Callable, Dict, List, Optional, Protocol, Union


class FunctionPayloadExtractor(Protocol):
    """
    FunctionPayloadExtractor specifies the interface for extracting function-calling payloads from LLM
    generated completions. Implementations of FunctionPayloadExtractor should be able to extract function names and
    arguments from LLM generated function calling completions/payloads.
    """

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


class DefaultPayloadExtractor(FunctionPayloadExtractor):
    """
    Implements a recursive search for extracting function payloads from complex and nested data structures.
    DefaultPayloadExtractor is designed to handle payloads that are dictionaries or lists by recursively
    searching for and extracting necessary fields as specified in the required_fields method.

    When encountering a non-dictionary or non-list payload, the extractor will attempt to convert the payload to a
    dictionary using the get_dict_converter method. If the payload is successfully converted, the extractor will
    continue the recursive search in the converted dictionary. This allows the extractor to handle payloads that are
    instances of dataclasses or other objects that can be converted to dictionaries (e.g. Pydantic models).
    """

    def __init__(self, arguments_field_name: str):
        self.arguments_field_name = arguments_field_name

    def extract_function_invocation(self, payload: Any) -> Dict[str, Any]:
        fields_and_values = self.search(payload)
        if fields_and_values:
            arguments = fields_and_values.get(self.arguments_field_name)
            if not isinstance(arguments, (str, dict)):
                raise ValueError(
                    f"Invalid {self.arguments_field_name} type {type(arguments)} for function call, expected str/dict"
                )
            return {
                "name": fields_and_values.get("name"),
                "arguments": json.loads(arguments) if isinstance(arguments, str) else arguments,
            }
        return {}

    def required_fields(self) -> List[str]:
        return ["name", self.arguments_field_name]

    def search(self, payload: Any) -> Dict[str, Any]:
        if self.is_primitive(payload):
            return {}

        if dict_converter := self.get_dict_converter(payload):
            payload = dict_converter()
        elif dataclasses.is_dataclass(payload):
            payload = dataclasses.asdict(payload)

        if isinstance(payload, dict):
            if all(field in payload for field in self.required_fields()):
                # this is the payload we are looking for
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

    def get_dict_converter(
        self, obj: Any, method_names: Optional[List[str]] = None
    ) -> Union[Callable[[], Dict[str, Any]], None]:
        method_names = method_names or ["model_dump", "dict"]  # search for pydantic v2 then v1
        for attr in method_names:
            if hasattr(obj, attr) and callable(getattr(obj, attr)):
                return getattr(obj, attr)
        return None

    def is_primitive(self, obj) -> bool:
        return isinstance(obj, (int, float, str, bool, type(None)))
