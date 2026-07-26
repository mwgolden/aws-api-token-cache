import pytest
from api_token_cache.models import ApiConfig, AuthMethod, ApiKeyAuth, ClientCredentialsAuth, DynamoDbConfig, CachedApiToken
from api_token_cache.token_cache import get_configuration, get_client_credentials, cache_token, get_cached_auth_token


BOT_NAME = "test_bot"
db_config =  DynamoDbConfig(
                api_config_table="ApiConfigTest",
                api_token_cache_table="ApiCacheTest"
            )



def test_no_auth(dynamodb):

    table = dynamodb.Table(db_config.api_config_table)

    item = {
        "bot_name": BOT_NAME,
        "config": {
            "requires_authentication": False , 
            "user_agent": "TestBot", 
            "http_method": "GET" 
        }
    }

    table.put_item(Item=item)

    result = get_configuration(bot_name=BOT_NAME, db_config=db_config)

    assert result.auth is None

def test_no_configuration(dynamodb):

    table = dynamodb.Table(db_config.api_config_table)

    bot_name = "bad_key"

    with pytest.raises(KeyError):
        result = get_configuration(bot_name=bot_name, db_config=db_config)

def test_client_credentials_oauth_config(dynamodb):
    item = {
        "bot_name": BOT_NAME,
        "config": {
            "requires_authentication" : True,
            "user_agent": "TestBot",
            "auth_endpoint": "https://www.somewhere.com/api/v1/access",
            "client_id": "test_api_client_id",
            "client_secret": "test_api_client_secret",
            "grant_type": "client_credentials",
            "http_method": "GET",
            "scope": "*"
        }
    }

    table = dynamodb.Table(db_config.api_config_table)
    table.put_item(Item=item)

    result = get_configuration(bot_name=BOT_NAME, db_config=db_config)
    assert isinstance(result.auth, ClientCredentialsAuth)


def test_api_key_auth(dynamodb):
    item = {
        "bot_name": BOT_NAME,
        "config": {
            "requires_authentication" : True,
            "user_agent": "TestBot",
            "http_method": "GET",
            "api_key": "123456789AbCdEfG",
            "authentication_method": "api_key"
        }
    }

    table = dynamodb.Table(db_config.api_config_table)
    table.put_item(Item=item)

    result = get_configuration(bot_name=BOT_NAME, db_config=db_config)
    assert isinstance(result.auth, ApiKeyAuth)
