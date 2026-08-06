import pytest
import time
import boto3
from api_token_cache.token_cache import cache_token
from api_token_cache.models import CachedApiToken


BOT_NAME = "test_bot"

@pytest.fixture
def cached_token():

    epoch_time = int(time.time())
    ttl_seconds =  86400
    expires = epoch_time + ttl_seconds
    
    return CachedApiToken(
        bot_name=BOT_NAME,
        access_token="123456789abdc!!",
        token_type= "bearer",
        scope="*",
        db_expires=expires
    )

def test_cache_token(dynamodb, db_config, cached_token):
    cache_token(token=cached_token, db_config=db_config)

    db = boto3.resource('dynamodb')
    db_table = db.Table(db_config.api_token_cache_table)

    result = db_table.query(
            Limit=1,
            KeyConditionExpression='bot_name=:botname',
            ExpressionAttributeValues={
                ':botname':BOT_NAME
            },
            ScanIndexForward=False
        )

    assert result["Count"] == 1
    
    item = dict(result['Items'][0])

    assert item["access_token"] == cached_token.access_token
    assert item["bot_name"] == cached_token.bot_name
    assert item["token_type"] == cached_token.token_type
    assert item["scope"] == cached_token.scope
    assert item["expires"] == cached_token.db_expires


