import pytest

from api_token_cache.token_cache import get_client_credentials


TEST_CLIENT_ID_PARAMETER = "test_api_client_id"
TEST_CLIENT_ID_VALUE = "TestAPIClient"
TEST_CLIENT_SECRET_PARAMETER = "test_api_client_secret"
TEST_CLIENT_SECRET_VALUE = "ItsASecret!"

def test_get_client_credentials(mock_ssm):
    client_id, secret = get_client_credentials(TEST_CLIENT_ID_PARAMETER, TEST_CLIENT_SECRET_PARAMETER)

    assert client_id == TEST_CLIENT_ID_VALUE
    assert secret == TEST_CLIENT_SECRET_VALUE


def test_get_client_credentials_client_does_not_exist(mock_ssm):

    with pytest.raises(mock_ssm.exceptions.ParameterNotFound):
        get_client_credentials("Invalid", TEST_CLIENT_SECRET_PARAMETER)

def test_get_client_credentials_secret_does_not_exist(mock_ssm):

    with pytest.raises(mock_ssm.exceptions.ParameterNotFound):
        get_client_credentials(TEST_CLIENT_ID_PARAMETER, "Invalid")