from typing import Any, Dict, List, Literal, Optional

from openapi_service_client.http_client import VALID_HTTP_METHODS


class Operation:

    def __init__(
        self,
        path: str,
        method: str,
        operation_dict: Dict[str, Any],
        spec_dict: Dict[str, Any],
    ):
        if method.lower() not in VALID_HTTP_METHODS:
            raise ValueError(f"Invalid HTTP method: {method}")
        self.path = path
        self.method = method.lower()
        self.operation_dict = operation_dict
        self.spec_dict = spec_dict

    def get_parameters(self, location: Optional[Literal["header", "query", "path"]] = None) -> List[Dict[str, Any]]:
        parameters = self.operation_dict.get("parameters", [])
        path_item = self.spec_dict.get("paths", {}).get(self.path, {})
        parameters.extend(path_item.get("parameters", []))
        if location:
            return [param for param in parameters if param["in"] == location]
        return parameters

    def get_request_body(self) -> Dict[str, Any]:
        return self.operation_dict.get("requestBody", {})

    def get_responses(self) -> Dict[str, Any]:
        return self.operation_dict.get("responses", {})

    def get_security_requirements(self) -> List[Dict[str, List[str]]]:
        # Try to get operation-specific security requirements first
        security_requirements = self.operation_dict.get("security", [])

        # If not present, default to the global security requirements
        if not security_requirements:
            security_requirements = self.spec_dict.get("security", [])

        return security_requirements

    def get_server_url(self) -> str:
        servers = self.operation_dict.get("servers", [])
        if not servers:
            servers = self.spec_dict.get("servers", [])
        if servers:
            return servers[0].get("url", "")
        return ""

    def get_field(self, key: str, default: Any = None) -> Any:
        return self.operation_dict.get(key, default)
