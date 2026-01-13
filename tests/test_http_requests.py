import json
import urllib3
from api_token_cache.http_requests import get_auth_token
from api_token_cache.models import ClientCredentialsAuth
from unittest.mock import MagicMock, patch

def test_get_auth_token(mock_ssm):
    user_agent = 'test_agent'
    client_credentials = ClientCredentialsAuth(
        "https://auth.test.com/token",
        scope="*",
        client_id="test_api_client_id",
        client_secret="test_api_client_secret",
        grant_type="client_credentials"
    )

    http = MagicMock(spec=urllib3.PoolManager)

    fake_response = MagicMock(spec=urllib3.response.HTTPResponse)
    fake_response.status = 200
    fake_response.data = json.dumps({
        "access_token": "1234567890ghghuyuokpoclkxdblBCVLKDgbyuvcvkdvnjknhis",
        "token_type": "Bearer",
        "expires_in": 3600
    }).encode("utf-8")

    http.request.return_value = fake_response

    token = get_auth_token(user_agent=user_agent, auth_config=client_credentials, http=http)

    keys = list(token.keys())
    assert token["access_token"] == "1234567890ghghuyuokpoclkxdblBCVLKDgbyuvcvkdvnjknhis"