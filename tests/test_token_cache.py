import boto3
import pytest
from moto import mock_aws
from api_token_cache.token_cache import get_configuration, get_client_credentials, cache_token, get_cached_auth_token


TABLE_NAME = "ApiConfigTest"
CACHE_TABLE_NAME = "ApiCacheTest"
BOT_NAME = "test_bot"

@pytest.fixture(scope="session")
def dynamodb():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        table = dynamodb.create_table( # type: ignore
            TableName=TABLE_NAME,
            KeySchema=[
                {"AttributeName": "bot_name", "KeyType": "HASH" }
            ],
            AttributeDefinitions=[
                { "AttributeName": "bot_name", "AttributeType": "S" }
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        cache_table = dynamodb.create_table(  # type: ignore
             TableName=CACHE_TABLE_NAME,
             KeySchema=[
                  {"AttributeName": "bot_name", "KeyType": "HASH"},
                  {"AttributeName": "expires", "KeyType": "RANGE"}
             ],
             AttributeDefinitions=[
                  { "AttributeName": "bot_name", "AttributeType": "S" },
                  { "AttributeName": "expires", "AttributeType": "N" }
             ],
            BillingMode="PAY_PER_REQUEST"
        )

        table.wait_until_exists()
        cache_table.wait_until_exists()
        yield dynamodb


CLIENT_ID = "TestAPIClient"
SECRET = "ItsASecret!"

@pytest.fixture(scope="session")
def mock_ssm():
    with mock_aws():
        ssm = boto3.client("ssm")
        ssm.put_parameter(
            Name="test_api_client_id",
            Description="client id",
            Value=CLIENT_ID,
            Type="String"
        )

        ssm.put_parameter(
            Name="test_api_client_secret",
            Description="client secret",
            Value=SECRET,
            Type="SecureString"
        )

        yield ssm
        

def test_get_configuration(dynamodb):

    table = dynamodb.Table(TABLE_NAME)

    item = {
        "bot_name": BOT_NAME,
        "config": {
            "requires_authentication": False , 
            "user_agent": "TestBot", 
            "http_method": "GET" 
        }
    }

    table.put_item(Item=item)

    result = get_configuration(bot_name=BOT_NAME, api_config_table=TABLE_NAME)

    assert result == item["config"]



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
    cache_token(
          bot_name=BOT_NAME,
          data=TEST_DATA,
          api_token_cache_table=CACHE_TABLE_NAME
     )

    response = get_cached_auth_token(
          bot_name=BOT_NAME,
          api_token_cache_table=CACHE_TABLE_NAME
     )
    
    assert response is not None
    assert set(response.keys()) == {"access_token", "token_type", "expires_in", "scope"}
    assert TEST_DATA['access_token'] == response['access_token']
    assert TEST_DATA['token_type'] == response['token_type']
    assert TEST_DATA['scope'] == response['scope']


def test_bot_isolation(dynamodb):
     response = get_cached_auth_token(
          bot_name="IDontExist",
          api_token_cache_table=CACHE_TABLE_NAME
     )

     assert response is None
