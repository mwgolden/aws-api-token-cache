import boto3
from api_token_cache.models import ApiConfig, AuthMethod, ApiKeyAuth, ClientCredentialsAuth, DynamoDbConfig, CachedApiToken
from typing import Optional, Tuple

def parse_api_config(config: dict) -> ApiConfig:
    user_agent = config["user_agent"]
    http_method = config["http_method"]
    grant_type = config.get("grant_type", None)
    if grant_type is None:
        return ApiConfig(
            user_agent=config["user_agent"],
            http_method=config["http_method"],
            auth=None
        )
    auth_method = AuthMethod(grant_type)
    if auth_method is AuthMethod.CLIENT_CREDENTIALS:
        auth = ClientCredentialsAuth(
                auth_endpoint=config["auth_endpoint"],
                scope=config["scope"],
                client_id=config["client_id"],
                client_secret=config["client_secret"],
                grant_type=config["grant_type"]
            )
    elif auth_method is AuthMethod.API_KEY:
        auth = ApiKeyAuth(api_key=config["api_key"])
    else:
        raise ValueError(f"Unsupported authentication method: {auth_method}")
    
    return ApiConfig(
        user_agent=user_agent,
        http_method=http_method,
        auth=auth
    )

def parse_token_cache_response(item: dict) -> CachedApiToken:
    cached_token = item["access_token"]
    bot_name = item["bot_name"]
    token_type = item["token_type"]
    scope = item["scope"]
    expires = item["expires"]
    
    return CachedApiToken(
        bot_name=bot_name,
        access_token=cached_token,
        token_type=token_type,
        scope=scope,
        db_expires=expires
    )


def get_configuration(bot_name: str, db_config: DynamoDbConfig) -> ApiConfig:
    """
    Get API configuration from DynamoDb table
    """
    db = boto3.resource('dynamodb')
    db_table = db.Table(db_config.api_config_table) # type: ignore
    response = db_table.get_item(
        Key={
            'bot_name': bot_name
        }
    )
    item = response.get("Item")
    if not item:
        raise KeyError(f"No configuration exists for bot: {bot_name}")
    config = item['config']
    return parse_api_config(config)
    

def get_cached_auth_token(bot_name: str, db_config: DynamoDbConfig) -> Optional[CachedApiToken]:
    """
    Get cached api token from DynamoDb Table
    """
    db = boto3.resource('dynamodb')
    db_table = db.Table(db_config.api_token_cache_table) # type: ignore
    result = db_table.query(
        Limit=1,
        KeyConditionExpression='bot_name=:botname',
        ExpressionAttributeValues={
            ':botname':bot_name
        },
        ScanIndexForward=False
    )
    if result['Count'] == 1:
        item = dict(result['Items'][0])
        return parse_token_cache_response(item)
    return None

def get_client_credentials(client_name: str, secret_name: str) -> Tuple[str, str]:
    """
    Get client id and secret stored in AWS Parameter Store
    """
    ssm_client = boto3.client('ssm')
    client_id = ssm_client.get_parameter(Name=client_name)
    client_secret = ssm_client.get_parameter(Name=secret_name, WithDecryption=True)
    return client_id['Parameter']['Value'], client_secret['Parameter']['Value']

def cache_token(token: CachedApiToken, db_config: DynamoDbConfig):
    """
    Persist an access token in DynamoDb table
    """
    
    db = boto3.resource('dynamodb')
    table = db.Table(db_config.api_token_cache_table) # type: ignore
    table.put_item(
        Item={
                "bot_name": token.bot_name,
                "expires": token.db_expires,
                "access_token": token.access_token,
                "token_type": token.token_type,
                "scope": token.scope
        }
    )
