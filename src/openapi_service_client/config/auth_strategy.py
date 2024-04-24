from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class AuthenticationStrategy(Protocol):
    """
    Represents an authentication strategy that can be applied to an HTTP request.
    """

    def apply_auth(self, security_scheme: Dict[str, Any], request: Dict[str, Any]):
        """
        Apply the authentication strategy to the given request.

        :param security_scheme: the security scheme from the OpenAPI spec.
        :param request: the request to apply the authentication to.
        """
        pass


class PassThroughAuthentication(AuthenticationStrategy):
    def apply_auth(self, security_scheme: Dict[str, Any], request: Dict[str, Any]):
        pass
