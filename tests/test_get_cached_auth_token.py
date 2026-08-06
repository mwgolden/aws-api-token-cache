import pytest
import time
from  api_token_cache.token_cache import get_cached_auth_token
from api_token_cache.models import CachedApiToken

BOT_NAME = "TESTBOT"

@pytest.fixture
def cached_token(dynamodb, db_config):
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

    return item

def test_get_cached_auth_token_returns_token(cached_token, db_config):
    result = get_cached_auth_token(bot_name=BOT_NAME, db_config=db_config)

    assert isinstance(result, CachedApiToken)
    assert result.bot_name == cached_token["bot_name"]
    assert result.token_type == cached_token["token_type"]
    assert result.access_token == cached_token["access_token"]
    assert result.scope == cached_token["scope"]
    assert result.db_expires == cached_token["expires"]


def test_get_cached_auth_token_returns_none(dynamodb, db_config):

    result = get_cached_auth_token(bot_name="BadName", db_config=db_config)

    assert result is None