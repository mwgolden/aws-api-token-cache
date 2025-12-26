import boto3
import pytest
from moto import mock_aws
from api_token_cache.token_cache import get_configuration


TABLE_NAME = "ApiConfigTest"
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

        table.wait_until_exists()
        yield dynamodb


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

