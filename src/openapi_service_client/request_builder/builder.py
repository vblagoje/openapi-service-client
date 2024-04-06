from typing import Any, Dict, Optional

from openapi_service_client.config import (
    AuthenticationStrategy,
    PassThroughAuthentication,
)
from openapi_service_client.http_client.client import AbstractHttpClient
from openapi_service_client.spec import OpenAPISpecification, Operation


class RequestBuilder:
    def __init__(
        self,
        openapi_parser: OpenAPISpecification,
        http_client: AbstractHttpClient,
        auth_config: Optional[AuthenticationStrategy] = None,
    ):
        self.openapi_parser = openapi_parser
        self.http_client = http_client
        self.auth_config = auth_config or PassThroughAuthentication()

    def build_request(self, operation: Operation, **kwargs) -> Any:
        url = self._build_url(operation, **kwargs)
        method = operation.method.lower()
        headers = self._build_headers(operation)
        query_params = self._build_query_params(operation, **kwargs)
        body = self._build_request_body(operation, **kwargs)

        request = {
            "url": url,
            "method": method,
            "headers": headers,
            "params": query_params,
            "json": body,
        }
        self._apply_authentication(operation, request)
        return request

    def _build_headers(self, operation: Operation, **kwargs) -> Dict[str, str]:
        headers = {}

        for parameter in operation.get_parameters("header"):
            param_value = kwargs.get(parameter["name"], None)
            if param_value:
                headers[parameter["name"]] = str(param_value)
            elif parameter.get("required", False):
                raise ValueError(f"Missing required header parameter: {parameter['name']}")
        return headers

    def _build_url(self, operation: Operation, **kwargs) -> str:
        server_url = operation.get_server_url()
        path = operation.path

        for parameter in operation.get_parameters("path"):
            param_value = kwargs.get(parameter["name"], None)
            if param_value:
                path = path.replace(f"{{{parameter['name']}}}", str(param_value))
            elif parameter.get("required", False):
                raise ValueError(f"Missing required path parameter: {parameter['name']}")

        return server_url + path

    def _build_query_params(self, operation: Operation, **kwargs) -> Dict[str, Any]:
        query_params = {}

        # Simplify query parameter assembly using _get_parameter_value
        for parameter in operation.get_parameters("query"):
            param_value = kwargs.get(parameter["name"], None)
            if param_value:
                query_params[parameter["name"]] = param_value
            elif parameter.get("required", False):
                raise ValueError(f"Missing required query parameter: {parameter['name']}")
        return query_params

    def _build_request_body(self, operation: Operation, **kwargs) -> Any:
        request_body = operation.get_request_body()

        if request_body:
            content = request_body.get("content", {})
            if "application/json" in content:
                return {**kwargs}
            raise NotImplementedError("Request body content type not supported")

        return None

    def _apply_authentication(self, operation: Operation, request: Dict[str, Any]):
        # security requirements specify which authentication scheme to apply
        # (the "what/which")
        security_requirements = operation.get_security_requirements()

        # security schemes define how to authenticate (the "how")
        security_schemes = operation.spec_dict.get("components", {}).get("securitySchemes", {})

        if security_requirements:
            for requirement in security_requirements:
                for scheme_name in requirement:
                    if scheme_name in security_schemes:
                        security_scheme = security_schemes[scheme_name]
                        self.auth_config.apply_auth(security_scheme, request)
                    break  # Assuming only one requirement needs to be satisfied
