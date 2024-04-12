import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Union

from openapi_service_client.config import (
    ApiKeyAuthentication,
    AuthenticationStrategy,
    HTTPAuthentication,
    HttpClientConfig,
    OAuthAuthentication,
    PassThroughAuthentication,
)
from openapi_service_client.http_client import AbstractHttpClient, RequestsHttpClient
from openapi_service_client.providers import LLMProvider, OpenAILLMProvider
from openapi_service_client.providers.payload_extractor import FunctionPayloadExtractor
from openapi_service_client.spec import OpenAPISpecification


class ClientConfiguration(Protocol):

    def get_http_client(self) -> AbstractHttpClient:
        pass

    def get_http_client_config(self) -> HttpClientConfig:
        pass

    def get_auth_config(self) -> AuthenticationStrategy:
        pass

    def get_openapi_spec(self) -> OpenAPISpecification:
        pass

    def get_tools_definitions(self) -> List[Dict[str, Any]]:
        pass

    def get_payload_extractor(self) -> FunctionPayloadExtractor:
        pass


class _DefaultOpenAPIServiceClientConfiguration(ClientConfiguration):

    def __init__(
        self,
        openapi_spec: Union[str, Path],
        credentials: Optional[Union[str, Dict[str, Any], AuthenticationStrategy]] = None,
        http_client: Optional[AbstractHttpClient] = None,
        http_client_config: Optional[HttpClientConfig] = None,
        provider: Optional[LLMProvider] = None,
    ):
        if isinstance(openapi_spec, (str, Path)) and os.path.isfile(openapi_spec):
            self.openapi_spec = OpenAPISpecification.from_file(openapi_spec)
        elif isinstance(openapi_spec, dict):
            self.openapi_spec = OpenAPISpecification.from_dict(openapi_spec)
        else:
            raise ValueError("Invalid OpenAPI specification format. Expected file path or dictionary.")

        self.credentials = credentials
        self.http_client = http_client or RequestsHttpClient(http_client_config)
        self.http_client_config = http_client_config or HttpClientConfig()
        self.provider = provider or OpenAILLMProvider()

    def get_openapi_spec(self) -> OpenAPISpecification:
        return self.openapi_spec

    def get_http_client(self) -> AbstractHttpClient:
        return self.http_client

    def get_http_client_config(self) -> HttpClientConfig:
        return self.http_client_config

    def get_tools_definitions(self) -> List[Dict[str, Any]]:
        return self.provider.get_schema_converter(self.openapi_spec).convert()

    def get_payload_extractor(self) -> FunctionPayloadExtractor:
        return self.provider.get_payload_extractor()

    def get_auth_config(self) -> AuthenticationStrategy:
        if self.credentials is None:
            return PassThroughAuthentication()

        if isinstance(self.credentials, AuthenticationStrategy):
            return self.credentials

        security_schemes = self.openapi_spec.get_security_schemes()
        if isinstance(self.credentials, str):
            return self._create_authentication_from_string(self.credentials, security_schemes)
        elif isinstance(self.credentials, dict):
            return self._create_authentication_from_dict(self.credentials)
        else:
            raise ValueError(f"Unsupported credentials type: {type(self.credentials)}")

    def _create_authentication_from_string(
        self, credentials: str, security_schemes: Dict[str, Any]
    ) -> AuthenticationStrategy:
        for _, scheme in security_schemes.items():
            if scheme["type"] == "apiKey":
                return ApiKeyAuthentication(api_key=credentials)
            elif scheme["type"] == "http":
                return HTTPAuthentication(token=credentials)
            elif scheme["type"] == "oauth2":
                return OAuthAuthentication(access_token=credentials)

        raise ValueError(f"Unable to create authentication from provided credentials: {credentials}")

    def _create_authentication_from_dict(self, credentials: Dict[str, Any]) -> AuthenticationStrategy:
        if "username" in credentials and "password" in credentials:
            return HTTPAuthentication(username=credentials["username"], password=credentials["password"])
        elif "api_key" in credentials:
            return ApiKeyAuthentication(api_key=credentials["api_key"])
        elif "token" in credentials:
            return HTTPAuthentication(token=credentials["token"])
        elif "access_token" in credentials:
            token_type = credentials.get("token_type", "Bearer")
            return OAuthAuthentication(access_token=credentials["access_token"], token_type=token_type)
        else:
            raise ValueError("Unable to create authentication from provided credentials: {credentials}")


class ClientConfigurationBuilder:
    def __init__(self):
        self._openapi_spec: Union[str, Path, None] = None
        self._credentials: Optional[Union[str, Dict[str, Any], AuthenticationStrategy]] = None
        self._http_client: Optional[AbstractHttpClient] = None
        self._http_client_config: Optional[HttpClientConfig] = None
        self._provider: Optional[LLMProvider] = None

    def with_openapi_spec(self, openapi_spec: Union[str, Path]) -> "ClientConfigurationBuilder":
        self._openapi_spec = openapi_spec
        return self

    def with_credentials(
        self, credentials: Union[str, Dict[str, Any], AuthenticationStrategy]
    ) -> "ClientConfigurationBuilder":
        self._credentials = credentials
        return self

    def with_http_client(self, http_client: AbstractHttpClient) -> "ClientConfigurationBuilder":
        self._http_client = http_client
        return self

    def with_http_client_config(self, http_client_config: HttpClientConfig) -> "ClientConfigurationBuilder":
        self._http_client_config = http_client_config
        return self

    def with_provider(self, provider: LLMProvider) -> "ClientConfigurationBuilder":
        self._provider = provider
        return self

    def build(self) -> ClientConfiguration:
        if self._openapi_spec is None:
            raise ValueError("OpenAPI specification must be provided to build a configuration.")

        return _DefaultOpenAPIServiceClientConfiguration(
            openapi_spec=self._openapi_spec,
            credentials=self._credentials,
            http_client=self._http_client,
            http_client_config=self._http_client_config,
            provider=self._provider,
        )
