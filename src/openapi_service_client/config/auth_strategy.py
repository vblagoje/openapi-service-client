from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict, Optional, Protocol, Union

if TYPE_CHECKING:
    from openapi_service_client.spec.open_api_spec import OpenAPISpecification  # F401


class AuthenticationStrategy(ABC):
    @abstractmethod
    def apply_auth(self, security_scheme: Dict[str, Any], request: Dict[str, Any]):
        pass


class PassThroughAuthentication(AuthenticationStrategy):
    def apply_auth(self, security_scheme: Dict[str, Any], request: Dict[str, Any]):
        pass


class AuthenticationFactory(Protocol):
    def create_authentication(
        self,
        openapi_spec: "OpenAPISpecification",
        credentials: Optional[Union[str, Dict[str, Any], AuthenticationStrategy]] = None,
    ) -> AuthenticationStrategy:
        """
        Create an authentication strategy based on the credentials and the OpenAPI specification.
        :param openapi_spec: The OpenAPI specification.
        :param credentials: The credentials to use for authentication.
        :return: An authentication strategy.
        """
        pass
