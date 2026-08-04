import pytest
from api_token_cache.token_cache import parse_api_config
from api_token_cache.models import ClientCredentialsAuth, ApiKeyAuth

@pytest.fixture
def client_credentials_config():
    return {
        "requires_authentication" : True,
        "user_agent": "TestBot",
        "auth_endpoint": "https://www.somewhere.com/api/v1/access",
        "client_id": "test_api_client_id",
        "client_secret": "test_api_client_secret",
        "grant_type": "client_credentials",
        "http_method": "GET",
        "scope": "*"
    }

@pytest.fixture
def api_key_config():
    return {
        "requires_authentication" : True,
        "user_agent": "TestBot",
        "http_method": "GET",
        "api_key": "123456789AbCdEfG",
        "authentication_method": "api_key"
    }

@pytest.fixture
def no_auth_config():
    return {
        "requires_authentication": False , 
        "user_agent": "TestBot", 
        "http_method": "GET" 
    }

@pytest.fixture
def invalid_auth_config():
    return {
            "requires_authentication" : True,
            "user_agent": "TestBot",
            "http_method": "GET",
            "authentication_method": "password"
    }
 

def test_return_client_credentials_auth_config(client_credentials_config):
    api_config = parse_api_config(config=client_credentials_config)

    assert isinstance(api_config.auth, ClientCredentialsAuth)


def test_return_api_key_auth_config(api_key_config):
    api_config= parse_api_config(config=api_key_config)

    assert isinstance(api_config.auth, ApiKeyAuth)


def test_return_config_without_auth(no_auth_config):
    api_config = parse_api_config(config=no_auth_config)

    assert api_config.auth is None 


def test_raise_unsupported_auth_error(invalid_auth_config):
    with pytest.raises(ValueError):
        parse_api_config(config=invalid_auth_config)

@pytest.mark.parametrize(
        "missing_fields", [
            "user_agent",
            "requires_authentication",
            "http_method",

        ]
)
def test_raises_with_require_fields_missing(missing_fields, client_credentials_config):
    del client_credentials_config[missing_fields]
    
    with pytest.raises(KeyError):
        parse_api_config(config=client_credentials_config)

@pytest.mark.parametrize(
          "missing_key", [
                "client_id",
                "client_secret",
                "scope",
                "auth_endpoint"
          ]
)
def test_raises_client_credentials_missing_required_fields(missing_key, client_credentials_config):
    del client_credentials_config[missing_key]

    with pytest.raises(KeyError):
        parse_api_config(config=client_credentials_config)


def test_raises_api_key_missing_required_fields(api_key_config):
    del api_key_config["api_key"]

    with pytest.raises(KeyError):
        parse_api_config(config=api_key_config)


def test_auth_required_but_no_method_defined(client_credentials_config):
    del client_credentials_config["grant_type"]

    with pytest.raises(ValueError, match="Authentication is required but no authentication type is configured"):
        parse_api_config(client_credentials_config)