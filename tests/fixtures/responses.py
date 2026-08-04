import pytest
import urllib3
import json
from unittest.mock import MagicMock


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
