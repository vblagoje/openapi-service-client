from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import (
    APIKeyCookie,
    APIKeyHeader,
    APIKeyQuery,
    HTTPAuthorizationCredentials,
    HTTPBasic,
    HTTPBasicCredentials,
    HTTPBearer,
)

from src.openapi_service_client import OpenAPIServiceClient
from src.openapi_service_client.config import ApiKeyAuthentication
from src.openapi_service_client.config.configuration import HTTPAuthentication
from tests.conftest import FastAPITestClient

API_KEY = "secret_api_key"
BASIC_AUTH_USERNAME = "admin"
BASIC_AUTH_PASSWORD = "secret_password"

API_KEY_QUERY = "secret_api_key_query"
API_KEY_COOKIE = "secret_api_key_cookie"
BEARER_TOKEN = "secret_bearer_token"

api_key_query = APIKeyQuery(name="api_key")
api_key_cookie = APIKeyCookie(name="api_key")
bearer_auth = HTTPBearer()

api_key_header = APIKeyHeader(name="X-API-Key")
basic_auth_http = HTTPBasic()


def create_greet_api_key_query_app() -> FastAPI:
    app = FastAPI()

    def api_key_query_auth(api_key: str = Depends(api_key_query)):
        if api_key != API_KEY_QUERY:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
        return api_key

    @app.get("/greet-api-key-query/{name}")
    def greet_api_key_query(name: str, api_key: str = Depends(api_key_query_auth)):
        greeting = f"Hello, {name} from api_key_query_auth, using {api_key}"
        return JSONResponse(content={"greeting": greeting})

    return app


def create_greet_api_key_cookie_app() -> FastAPI:
    app = FastAPI()

    def api_key_cookie_auth(api_key: str = Depends(api_key_cookie)):
        if api_key != API_KEY_COOKIE:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
        return api_key

    @app.get("/greet-api-key-cookie/{name}")
    def greet_api_key_cookie(name: str, api_key: str = Depends(api_key_cookie_auth)):
        greeting = f"Hello, {name} from api_key_cookie_auth, using {api_key}"
        return JSONResponse(content={"greeting": greeting})

    return app


def create_greet_bearer_auth_app() -> FastAPI:
    app = FastAPI()

    def bearer_auth_scheme(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_auth),  # noqa: B008
    ):
        if credentials.scheme != "Bearer" or credentials.credentials != BEARER_TOKEN:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return credentials.credentials

    @app.get("/greet-bearer-auth/{name}")
    def greet_bearer_auth(name: str, token: str = Depends(bearer_auth_scheme)):
        greeting = f"Hello, {name} from bearer_auth, using {token}"
        return JSONResponse(content={"greeting": greeting})

    return app


def create_greet_api_key_auth_app() -> FastAPI:
    app = FastAPI()

    def api_key_auth(api_key: str = Depends(api_key_header)):
        if api_key != API_KEY:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
        return api_key

    @app.get("/greet-api-key/{name}")
    def greet_api_key(name: str, api_key: str = Depends(api_key_auth)):
        greeting = f"Hello, {name} from api_key_auth, using {api_key}"
        return JSONResponse(content={"greeting": greeting})

    return app


def create_greet_basic_auth_app() -> FastAPI:
    app = FastAPI()

    def basic_auth(credentials: HTTPBasicCredentials = Depends(basic_auth_http)):  # noqa: B008
        if credentials.username != BASIC_AUTH_USERNAME or credentials.password != BASIC_AUTH_PASSWORD:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return credentials.username

    @app.get("/greet-basic-auth/{name}")
    def greet_basic_auth(name: str, username: str = Depends(basic_auth)):
        greeting = f"Hello, {name} from basic_auth, using {username}"
        return JSONResponse(content={"greeting": greeting})

    return app


class TestOpenAPIAuth:

    def test_greet_api_key_auth(self, test_files_path):
        client = OpenAPIServiceClient(
            test_files_path / "openapi_greeting_service.yml",
            FastAPITestClient(create_greet_api_key_auth_app()),
            ApiKeyAuthentication(API_KEY),
        )
        payload = {
            "id": "call_NJr1NBz2Th7iUWJpRIJZoJIA",
            "function": {
                "arguments": '{"name": "John"}',
                "name": "greetApiKey",
            },
            "type": "function",
        }
        response = client.invoke(payload)
        assert response == {"greeting": "Hello, John from api_key_auth, using secret_api_key"}

    def test_greet_basic_auth(self, test_files_path):
        client = OpenAPIServiceClient(
            test_files_path / "openapi_greeting_service.yml",
            FastAPITestClient(create_greet_basic_auth_app()),
            HTTPAuthentication(BASIC_AUTH_USERNAME, BASIC_AUTH_PASSWORD),
        )
        payload = {
            "id": "call_NJr1NBz2Th7iUWJpRIJZoJIA",
            "function": {
                "arguments": '{"name": "John"}',
                "name": "greetBasicAuth",
            },
            "type": "function",
        }
        response = client.invoke(payload)
        assert response == {"greeting": "Hello, John from basic_auth, using admin"}

    def test_greet_api_key_query_auth(self, test_files_path):
        client = OpenAPIServiceClient(
            test_files_path / "openapi_greeting_service.yml",
            FastAPITestClient(create_greet_api_key_query_app()),
            ApiKeyAuthentication(API_KEY_QUERY),
        )
        payload = {
            "id": "call_NJr1NBz2Th7iUWJpRIJZoJIA",
            "function": {
                "arguments": '{"name": "John"}',
                "name": "greetApiKeyQuery",
            },
            "type": "function",
        }
        response = client.invoke(payload)
        assert response == {"greeting": "Hello, John from api_key_query_auth, using secret_api_key_query"}

    def test_greet_api_key_cookie_auth(self, test_files_path):
        client = OpenAPIServiceClient(
            test_files_path / "openapi_greeting_service.yml",
            FastAPITestClient(create_greet_api_key_cookie_app()),
            ApiKeyAuthentication(API_KEY_COOKIE),
        )
        payload = {
            "id": "call_NJr1NBz2Th7iUWJpRIJZoJIA",
            "function": {
                "arguments": '{"name": "John"}',
                "name": "greetApiKeyCookie",
            },
            "type": "function",
        }
        response = client.invoke(payload)
        assert response == {"greeting": "Hello, John from api_key_cookie_auth, using secret_api_key_cookie"}

    def test_greet_bearer_auth(self, test_files_path):
        client = OpenAPIServiceClient(
            test_files_path / "openapi_greeting_service.yml",
            FastAPITestClient(create_greet_bearer_auth_app()),
            HTTPAuthentication(token=BEARER_TOKEN),
        )
        payload = {
            "id": "call_NJr1NBz2Th7iUWJpRIJZoJIA",
            "function": {
                "arguments": '{"name": "John"}',
                "name": "greetBearerAuth",
            },
            "type": "function",
        }
        response = client.invoke(payload)
        assert response == {"greeting": "Hello, John from bearer_auth, using secret_bearer_token"}