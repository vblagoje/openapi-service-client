import logging
from typing import Any, Dict, List, Optional

import yaml

from ..http_client import VALID_HTTP_METHODS
from .operation import Operation

logger = logging.getLogger(__name__)


class OpenAPISpecification:
    def __init__(self, spec_dict: Dict[str, Any]):
        self.spec_dict = spec_dict

    @classmethod
    def from_file(cls, spec_file: str) -> "OpenAPISpecification":
        with open(spec_file, "r") as file:
            loaded_spec = yaml.safe_load(file)
            return cls(loaded_spec)

    def get_paths(self) -> Dict[str, Dict[str, Any]]:
        return self.spec_dict.get("paths", {})

    def get_operation(self, path: str, method: Optional[str] = None) -> Operation:
        path_item = self.get_paths().get(path, {})
        return self.get_operation_item(path, path_item, method)

    def find_operation_by_path_substring(
        self, path_partial: str, method: Optional[str] = None
    ) -> Operation:
        for path, path_item in self.get_paths().items():
            if path_partial in path:
                return self.get_operation_item(path, path_item, method)
        raise ValueError(f"No operation found with path containing {path_partial}")

    def find_operation_by_id(
        self, op_id: str, method: Optional[str] = None
    ) -> Operation:
        for path, path_item in self.get_paths().items():
            op: Operation = self.get_operation_item(path, path_item, method)
            if op_id in op.get_field("operationId", ""):
                return self.get_operation_item(path, path_item, method)
        raise ValueError(f"No operation found with operationId {op_id}")

    def get_operation_item(
        self, path: str, path_item: Dict[str, Any], method: Optional[str] = None
    ) -> Operation:
        if method:
            operation_dict = path_item.get(method.lower(), {})
            if not operation_dict:
                raise ValueError(
                    f"No operation found for method {method} at path {path}"
                )
            return Operation(path, method.lower(), operation_dict, self.spec_dict)
        else:
            # If method is not specified, check the number of operations under
            # the path.
            if len(path_item) == 1:
                # Only one operation exists, return it.
                method, operation_dict = next(iter(path_item.items()))
                return Operation(path, method, operation_dict, self.spec_dict)
            elif len(path_item) > 1:
                raise ValueError(
                    f"Multiple operations found at path {path}, method parameter is required."
                )
            else:
                raise ValueError(f"No operations found at path {path}.")

    def get_operations(self) -> List[Operation]:
        operations = []
        for path, path_item in self.get_paths().items():
            for method, operation_dict in path_item.items():
                if method.lower() in VALID_HTTP_METHODS:
                    operations.append(
                        Operation(path, method, operation_dict, self.spec_dict)
                    )
                else:
                    logger.warning(
                        f"Skipping operation with invalid HTTP method: {method}"
                    )
        return operations

    def get_security_schemes(self) -> Dict[str, Dict[str, Any]]:
        components = self.spec_dict.get("components", {})
        return components.get("securitySchemes", {})

    @classmethod
    def from_dict(cls, spec_dict: Dict[str, Any]) -> "OpenAPISpecification":
        parser = cls({})
        parser.spec_dict = spec_dict
        return parser
