import pytest
import time
from  api_token_cache.token_cache import get_cached_auth_token
from api_token_cache.models import CachedApiToken

BOT_NAME = "TESTBOT"

def test_get_cached_auth_token_returns_token(dynamodb, db_config):
    table = dynamodb.Table(db_config.api_token_cache_table)

    epoch_time = int(time.time())
    ttl_seconds =  86400
    expires = epoch_time + ttl_seconds
    item = {
        "bot_name": BOT_NAME,
        "token_type": "bearer",
        "access_token": "1234567890ghghuyuokpoclkxdblBCVLKDgbyuvcvkdvnjknhis",
        "scope": "*",
        "expires": expires
    }

    table.put_item(Item=item)

    result = get_cached_auth_token(bot_name=BOT_NAME, db_config=db_config)

    assert isinstance(result, CachedApiToken)