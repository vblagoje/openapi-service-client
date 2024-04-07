from typing import Any, Dict, Optional, Union

from openapi_service_client.config import (
    ApiKeyAuthentication,
    AuthenticationStrategy,
    HTTPAuthentication,
    OAuthAuthentication,
    PassThroughAuthentication,
)
from openapi_service_client.spec import OpenAPISpecification


class AuthenticationFactoryRegistry:
    _instance = None
    _factory = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
            cls._factory = DefaultAuthenticationFactory()
        return cls._instance

    def get_factory(self):
        return self._factory

    def set_factory(self, new_factory):
        self._factory = new_factory


class DefaultAuthenticationFactory:

    def create_authentication(
        self,
        openapi_spec: OpenAPISpecification,
        credentials: Optional[Union[str, Dict[str, Any], AuthenticationStrategy]] = None,
    ) -> AuthenticationStrategy:

        if credentials is None:
            return PassThroughAuthentication()

        if isinstance(credentials, AuthenticationStrategy):
            return credentials

        security_schemes = openapi_spec.get_security_schemes()
        if isinstance(credentials, str):
            return self._create_authentication_from_string(credentials, security_schemes)
        elif isinstance(credentials, dict):
            return self._create_authentication_from_dict(credentials)
        else:
            raise ValueError(f"Unsupported credentials type: {type(credentials)}")

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
