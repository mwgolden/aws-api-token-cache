import json
import sys
import time
from api_token_cache.token_cache import get_configuration, get_client_credentials, cache_token, get_cached_auth_token
from urllib3.util import make_headers
from urllib3.poolmanager import PoolManager
from api_token_cache.models import DynamoDbConfig, CachedApiToken, ClientCredentialsAuth

def get_auth_token(user_agent: str, auth_config: ClientCredentialsAuth, http: PoolManager) -> dict:
    """
    Authenticate with an API using basic authentication and return an authentication token 
    """
    client_id, client_secret = get_client_credentials(
            client_name=auth_config.client_id, secret_name=auth_config.client_secret
        )
    client_auth = make_headers(basic_auth=f"{client_id}:{client_secret}")
    data = {"grant_type":auth_config.grant_type, "scope":auth_config.scope, "X-Modhash": "xF3123"} 
    headers = {"User-Agent": user_agent, **client_auth}
    http_response = http.request(
        "POST",
        auth_config.auth_endpoint,
        headers=headers,
        fields=data
    )
    return http_response.json()

def http_oauth_client_credentials(url:str, bot_name:str, db_config:DynamoDbConfig, http:PoolManager) -> dict:
    bot_config = get_configuration(bot_name=bot_name, db_config=db_config)

    cached_token = get_cached_auth_token(bot_name=bot_name, db_config=db_config)

    if not cached_token:
        if isinstance(bot_config.auth, ClientCredentialsAuth):
            token = get_auth_token(user_agent=bot_config.user_agent, auth_config=bot_config.auth, http=http)
        else:
            raise TypeError(f"ClientCredentialsAuth is required, attempted to use {type(bot_config.auth).__name__}")
        
        if 'expires_in' in token:
            epoch_time = int(time.time())
            ttl_seconds =  token['expires_in']
            db_expires = epoch_time + ttl_seconds
        else:
            db_expires = sys.maxsize

        try:
            access_token=token["access_token"]
        except:
            raise KeyError("Auth response is missing access_token")

        cached_token = CachedApiToken(
            bot_name=bot_name,
            access_token=access_token,
            token_type=token.get("token_type", "Bearer"),
            scope=token.get("scope", "*"),
            db_expires=db_expires
        )
        cache_token(token=cached_token, db_config=db_config) # type: ignore
    
    headers = {
        "Authorization": f"Bearer {cached_token.access_token}",
        "User-Agent": f"{bot_config.user_agent}"
    }

    response = http.request(
        bot_config.http_method,
        url,
        headers=headers
    )

    return response.json()
