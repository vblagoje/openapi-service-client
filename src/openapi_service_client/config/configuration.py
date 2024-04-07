from base64 import b64encode
from typing import Any, Dict, Optional

from pydantic import Field
from pydantic_settings import BaseSettings

from openapi_service_client.config import AuthenticationStrategy


class ApiKeyAuthSettings(BaseSettings):
    api_key: Optional[str] = None


class ApiKeyAuthentication(AuthenticationStrategy):
    def __init__(self, api_key: Optional[str] = None):
        # Initialize settings, potentially from environment variables
        self.settings = ApiKeyAuthSettings()
        # Direct settings initialization
        if api_key is not None:
            self.settings.api_key = api_key

        if self.settings.api_key is None:
            raise ValueError("API key must be provided either via parameter or environment variable")

    def apply_auth(self, security_scheme: Dict[str, Any], request: Dict[str, Any]):
        if security_scheme["in"] == "header":
            request.setdefault("headers", {})[security_scheme["name"]] = self.settings.api_key
        elif security_scheme["in"] == "query":
            request.setdefault("params", {})[security_scheme["name"]] = self.settings.api_key
        elif security_scheme["in"] == "cookie":
            request.setdefault("cookies", {})[security_scheme["name"]] = self.settings.api_key
        else:
            raise ValueError(
                f"Unsupported apiKey authentication location: {security_scheme['in']}, "
                f"must be one of 'header', 'query', or 'cookie'"
            )


class HTTPAuthSettings(BaseSettings):
    username: Optional[str] = None
    password: Optional[str] = None
    token: Optional[str] = None


class HTTPAuthentication(AuthenticationStrategy):
    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
    ):
        self.settings = HTTPAuthSettings(username=username, password=password, token=token)

        if not self.settings.token and (not self.settings.username or not self.settings.password):
            raise ValueError(
                "For HTTP Basic Auth, both username and password must be provided. "
                "For Bearer Auth, a token must be provided."
            )

    def apply_auth(self, security_scheme: Dict[str, Any], request: Dict[str, Any]):
        if security_scheme["type"] == "http":
            if security_scheme["scheme"].lower() == "basic":
                if not self.settings.username or not self.settings.password:
                    raise ValueError("Username and password must be provided for Basic Auth.")
                credentials = f"{self.settings.username}:{self.settings.password}"
                encoded_credentials = b64encode(credentials.encode("utf-8")).decode("utf-8")
                request.setdefault("headers", {})["Authorization"] = f"Basic {encoded_credentials}"
            elif security_scheme["scheme"].lower() == "bearer":
                if not self.settings.token:
                    raise ValueError("Token must be provided for Bearer Auth.")
                request.setdefault("headers", {})["Authorization"] = f"Bearer {self.settings.token}"
            else:
                raise ValueError(f"Unsupported HTTP authentication scheme: {security_scheme['scheme']}")
        else:
            raise ValueError("HTTPAuthentication strategy received a non-HTTP security scheme.")


class OAuthSettings(BaseSettings):
    access_token: Optional[str] = None
    token_type: Optional[str] = None


class OAuthAuthentication(AuthenticationStrategy):
    def __init__(self, access_token: Optional[str] = None, token_type: Optional[str] = None):
        self.settings = OAuthSettings(access_token=access_token, token_type=token_type)

        if not self.settings.access_token:
            raise ValueError("Access token must be provided for OAuth authentication.")

    def apply_auth(self, security_scheme: Dict[str, Any], request: Dict[str, Any]):
        if security_scheme["type"] == "oauth2":
            token_type = self.settings.token_type or "Bearer"
            request.setdefault("headers", {})["Authorization"] = f"{token_type} {self.settings.access_token}"
        else:
            raise ValueError("OAuthAuthentication strategy received a non-OAuth2 security scheme.")


class HttpClientConfig(BaseSettings):
    timeout: int = 10
    max_retries: int = 3
    default_headers: Dict[str, str] = Field(default_factory=dict)


class LoggingConfig(BaseSettings):
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "app.log"


class OpenAPIServiceClientConfiguration(BaseSettings):
    http_client: HttpClientConfig = Field(default_factory=HttpClientConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
