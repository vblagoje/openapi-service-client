from typing import Any, Dict, Protocol, runtime_checkable


@runtime_checkable
class AuthenticationStrategy(Protocol):
    def apply_auth(self, security_scheme: Dict[str, Any], request: Dict[str, Any]):
        pass


class PassThroughAuthentication(AuthenticationStrategy):
    def apply_auth(self, security_scheme: Dict[str, Any], request: Dict[str, Any]):
        pass
