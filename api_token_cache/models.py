from dataclasses import dataclass
from typing import Optional, Union
from enum import Enum

class AuthMethod(Enum):
    CLIENT_CREDENTIALS = "client_credentials"
    API_KEY = "api_key"

@dataclass
class ClientCredentialsAuth:
    auth_endpoint: str
    scope: str
    client_id: str
    client_secret: str

@dataclass
class ApiKeyAuth:
    api_key: str

@dataclass
class ApiConfig:
    user_agent: str
    http_method: str
    auth: Optional[Union[ClientCredentialsAuth, ApiKeyAuth]] = None

@dataclass
class DynamoDbConfig:
    api_config_table: str
    api_token_cache_table: str

@dataclass
class CachedApiToken:
    bot_name: str
    access_token: str
    token_type: str
    scope: str
    expires: float