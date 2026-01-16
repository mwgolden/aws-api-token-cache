import boto3
import pytest
import time
from moto import mock_aws
from api_token_cache.models import ApiConfig, AuthMethod, ApiKeyAuth, ClientCredentialsAuth, DynamoDbConfig, CachedApiToken
from api_token_cache.token_cache import get_configuration, get_client_credentials, cache_token, get_cached_auth_token


BOT_NAME = "test_bot"
db_config =  DynamoDbConfig(
                api_config_table="ApiConfigTest",
                api_token_cache_table="ApiCacheTest"
            )



def test_get_configuration(dynamodb):

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

    assert result.user_agent == "TestBot"

CLIENT_ID = "TestAPIClient"
SECRET = "ItsASecret!"

def test_get_client_credentials(mock_ssm):
         client_name = "test_api_client_id"
         secret_name = "test_api_client_secret"
         client_id, client_secret = get_client_credentials(client_name, secret_name)

         assert CLIENT_ID == client_id
         assert SECRET == client_secret


TEST_DATA = {
    'access_token': '1234567890ghghuyuokpoclkxdblBCVLKDgbyuvcvkdvnjknhis',
    'token_type': 'bearer',
    'expires_in': 86400,
    'scope': '*'
}

def test_cache_token_retrieval(dynamodb):

    epoch_time = int(time.time())
    ttl_seconds =  86400
    expires = epoch_time + ttl_seconds

    token = CachedApiToken(
         bot_name=BOT_NAME,
         token_type="bearer",
         access_token="1234567890ghghuyuokpoclkxdblBCVLKDgbyuvcvkdvnjknhis",
         scope="*",
         db_expires=expires
    )


    cache_token(
        token=token,
        db_config=db_config
    )

    response = get_cached_auth_token(
          bot_name=BOT_NAME,
          db_config=db_config
     )
    
    assert response is not None
    assert response.access_token == token.access_token


def test_bot_isolation(dynamodb):
     response = get_cached_auth_token(
          bot_name="IDontExist",
            db_config=db_config
     )

     assert response is None
