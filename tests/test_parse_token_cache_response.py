import pytest
from api_token_cache.token_cache import parse_token_cache_response
from api_token_cache.models import CachedApiToken

@pytest.fixture
def cached_api_token():
    return {
        "bot_name": "TESTBOT",
        "access_token": "1234567890ghghuyuokpoclkxdblBCVLKDgbyuvcvkdvnjknhis",
        "token_type": "bearer",
        "expires": 86400,
        "scope": "*"
    }

@pytest.mark.parametrize(
        "missing_fields", [
            "access_token",
            "token_type",
            "expires",
            "scope",
            "bot_name"
        ]
)
def test_parse_token_cache_response_raise_required_fields_missing(missing_fields, cached_api_token):
    del cached_api_token[missing_fields]

    with pytest.raises(KeyError):
        parse_token_cache_response(cached_api_token)

def test_parse_token_cache_response_valid_cached_api_token(cached_api_token):
    token = parse_token_cache_response(cached_api_token)

    assert isinstance(token, CachedApiToken)
    assert token.bot_name == cached_api_token["bot_name"]
    assert token.access_token == cached_api_token["access_token"]
    assert token.token_type == cached_api_token["token_type"]
    assert token.db_expires == cached_api_token["expires"]
    assert token.scope == cached_api_token["scope"]
