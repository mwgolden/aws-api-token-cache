import os
import pytest
import urllib3
import json
import boto3
from moto import mock_aws
from unittest.mock import MagicMock
from api_token_cache.models import  DynamoDbConfig

@pytest.fixture(scope="session", autouse=True)
def aws_creds():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


from moto import mock_aws
import boto3

@pytest.fixture(scope="session")
def mock_ssm():
    with mock_aws():
        ssm = boto3.client("ssm")
        ssm.put_parameter(
            Name="test_api_client_id",
            Description="client id",
            Value="TestAPIClient",
            Type="String"
        )

        ssm.put_parameter(
            Name="test_api_client_secret",
            Description="client secret",
            Value="ItsASecret!",
            Type="SecureString"
        )

        yield ssm

@pytest.fixture(scope="session")
def http_pool():
    return MagicMock(urllib3.PoolManager)


@pytest.fixture(scope="session")
def oauth_token_response():
    response = MagicMock(spec=urllib3.response.HTTPResponse)
    response.status = 200
    response.data = json.dumps({
        "access_token": "1234567890ghghuyuokpoclkxdblBCVLKDgbyuvcvkdvnjknhis",
        "token_type": "Bearer",
        "expires_in": 3600
    }).encode("utf-8")

    return response

@pytest.fixture(scope="session")
def api_response():
    response = MagicMock(spec=urllib3.response.HTTPResponse)
    response.status = 200
    response.data = json.dumps({
        "id": "123",
        "data": "some_data"
    }).encode("utf-8")

    return response

BOT_NAME = "test_bot"
db_config =  DynamoDbConfig(
                api_config_table="ApiConfigTest",
                api_token_cache_table="ApiCacheTest"
            )

@pytest.fixture(scope="session")
def dynamodb():
    with mock_aws():
        dynamodb = boto3.resource("dynamodb", region_name="us-east-1")

        table = dynamodb.create_table( # type: ignore
            TableName=db_config.api_config_table,
            KeySchema=[
                {"AttributeName": "bot_name", "KeyType": "HASH" }
            ],
            AttributeDefinitions=[
                { "AttributeName": "bot_name", "AttributeType": "S" }
            ],
            BillingMode="PAY_PER_REQUEST"
        )

        cache_table = dynamodb.create_table(  # type: ignore
             TableName=db_config.api_token_cache_table,
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