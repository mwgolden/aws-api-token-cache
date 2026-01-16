import json
import urllib3
from api_token_cache.http_requests import get_auth_token, http_oauth_client_credentials
from api_token_cache.models import ClientCredentialsAuth, DynamoDbConfig
from unittest.mock import MagicMock, patch

def test_get_auth_token(mock_ssm, http_pool, oauth_token_response):
    user_agent = 'test_agent'
    client_credentials = ClientCredentialsAuth(
        "https://auth.test.com/token",
        scope="*",
        client_id="test_api_client_id",
        client_secret="test_api_client_secret",
        grant_type="client_credentials"
    )

    http_pool.request.return_value = oauth_token_response

    token = get_auth_token(user_agent=user_agent, auth_config=client_credentials, http=http_pool)

    assert token["access_token"] == "1234567890ghghuyuokpoclkxdblBCVLKDgbyuvcvkdvnjknhis"


def test_http_oauth_client_credentials(mock_ssm, dynamodb, http_pool, api_response, oauth_token_response):

    db_config =  DynamoDbConfig(
                api_config_table="ApiConfigTest",
                api_token_cache_table="ApiCacheTest"
            )


    table = dynamodb.Table(db_config.api_config_table)

    item = {
        "bot_name": "test_bot",
        "config": {
            "auth_endpoint": "https://auth.test.com/token" , 
            "client_id": "test_api_client_id", 
            "client_secret": "test_api_client_secret",
            "grant_type": "client_credentials",
            "http_method": "GET",
            "scope": "*",
            "user_agent": "TestBot"
        }
    }

    table.put_item(Item=item)

    url = "http://someapi/get_data/"
    
    http_pool.request.side_effect = [oauth_token_response, api_response]
    
    response = http_oauth_client_credentials(url=url, bot_name="test_bot", db_config=db_config, http=http_pool)

    assert response["id"] == '123'
    assert response["data"] == "some_data"