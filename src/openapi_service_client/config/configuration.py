from base64 import b64encode
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from openapi_service_client.config import AuthenticationStrategy


@dataclass
class ApiKeyAuthentication(AuthenticationStrategy):
    api_key: Optional[str] = None

    def apply_auth(self, security_scheme: Dict[str, Any], request: Dict[str, Any]):
        if security_scheme["in"] == "header":
            request.setdefault("headers", {})[security_scheme["name"]] = self.api_key
        elif security_scheme["in"] == "query":
            request.setdefault("params", {})[security_scheme["name"]] = self.api_key
        elif security_scheme["in"] == "cookie":
            request.setdefault("cookies", {})[security_scheme["name"]] = self.api_key
        else:
            raise ValueError(
                f"Unsupported apiKey authentication location: {security_scheme['in']}, "
                f"must be one of 'header', 'query', or 'cookie'"
            )


@dataclass
class HTTPAuthentication(AuthenticationStrategy):
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None

    def __post_init__(self):
        if not self.token and (not self.username or not self.password):
            raise ValueError(
                "For HTTP Basic Auth, both username and password must be provided. "
                "For Bearer Auth, a token must be provided."
            )

    def apply_auth(self, security_scheme: Dict[str, Any], request: Dict[str, Any]):
        if security_scheme["type"] == "http":
            if security_scheme["scheme"].lower() == "basic":
                if not self.username or not self.password:
                    raise ValueError("Username and password must be provided for Basic Auth.")
                credentials = f"{self.username}:{self.password}"
                encoded_credentials = b64encode(credentials.encode("utf-8")).decode("utf-8")
                request.setdefault("headers", {})["Authorization"] = f"Basic {encoded_credentials}"
            elif security_scheme["scheme"].lower() == "bearer":
                if not self.token:
                    raise ValueError("Token must be provided for Bearer Auth.")
                request.setdefault("headers", {})["Authorization"] = f"Bearer {self.token}"
            else:
                raise ValueError(f"Unsupported HTTP authentication scheme: {security_scheme['scheme']}")
        else:
            raise ValueError("HTTPAuthentication strategy received a non-HTTP security scheme.")


@dataclass
class OAuthAuthentication(AuthenticationStrategy):
    access_token: Optional[str] = None
    token_type: Optional[str] = None

    def __post_init__(self):
        if not self.access_token:
            raise ValueError("Access token must be provided for OAuth authentication.")

    def apply_auth(self, security_scheme: Dict[str, Any], request: Dict[str, Any]):
        if security_scheme["type"] == "oauth2":
            token_type = self.token_type or "Bearer"
            request.setdefault("headers", {})["Authorization"] = f"{token_type} {self.access_token}"
        else:
            raise ValueError("OAuthAuthentication strategy received a non-OAuth2 security scheme.")


@dataclass
class HttpClientConfig:
    timeout: int = 10
    max_retries: int = 3
    default_headers: Dict[str, str] = field(default_factory=dict)
