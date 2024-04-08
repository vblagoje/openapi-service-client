from abc import ABC, abstractmethod
from typing import Any, Dict


class AuthenticationStrategy(ABC):
    @abstractmethod
    def apply_auth(self, security_scheme: Dict[str, Any], request: Dict[str, Any]):
        pass


class PassThroughAuthentication(AuthenticationStrategy):
    def apply_auth(self, security_scheme: Dict[str, Any], request: Dict[str, Any]):
        pass
