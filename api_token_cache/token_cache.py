import boto3
import time
import sys

def get_configuration(bot_name: str, api_config_table: str):
    """
    Get API configuration from DynamoDb table
    """
    db = boto3.resource('dynamodb')
    db_table = db.Table(api_config_table) # type: ignore
    response = db_table.get_item(
        Key={
            'bot_name': bot_name
        }
    )
    return response['Item']['config']

def get_cached_auth_token(bot_name: str, api_token_cache_table: str):
    """
    Get cached api token from DynamoDb Table
    """
    db = boto3.resource('dynamodb')
    db_table = db.Table(api_token_cache_table) # type: ignore
    response = db_table.query(
        Limit=1,
        KeyConditionExpression='bot_name=:botname',
        ExpressionAttributeValues={
            ':botname':bot_name
        },
        ScanIndexForward=False
    )
    if response['Count'] == 1:
        response = response['Items'][0]['access_token']
        epoch_time = int(time.time())
        exp_date = response['Items'][0]['expires']
        response['expires_in'] = exp_date - epoch_time
        return response
    return None

def get_client_credentials(client_name, secret_name):
    """
    Get client id and secret stored in AWS Parameter Store
    """
    ssm_client = boto3.client('ssm')
    client_id = ssm_client.get_parameter(Name=client_name)
    client_secret = ssm_client.get_parameter(Name=secret_name, WithDecryption=True)
    return client_id['Parameter']['Value'], client_secret['Parameter']['Value']

def cache_token(bot_name, data, api_token_cache_table):
    """
    Cache an access token in DynamoDb table
    """
    if 'expires_in' in data.keys():
        epoch_time = int(time.time())
        ttl_seconds =  data['expires_in']
        expires_on = epoch_time + ttl_seconds
    else:
        expires_on = sys.maxsize
        data['expires_in'] = expires_on
    db = boto3.resource('dynamodb')
    table = db.Table(api_token_cache_table) # type: ignore
    table.put_item(
        Item={
                'bot_name': bot_name,
                'expires': expires_on,
                'access_token': data
        }
    )
