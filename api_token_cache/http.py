import json
from urllib3.util import make_headers
from urllib3.poolmanager import PoolManager

def get_auth_token(client_id: str, client_secret: str, config: dict, http: PoolManager) -> dict:
    """
    Authenticate with an API using basic authentication and return an authentication token 
    """
    client_auth = make_headers(basic_auth=f"{client_id}:{client_secret}")
    data = {"grant_type":config['grant_type'], "scope": config['scope'], "X-Modhash": "xF3123"}
    headers = {"User-Agent": config['user_agent'], **client_auth}
    http_response = http.request(
        "POST",
        config['auth_endpoint'],
        headers=headers,
        fields=data
    )
    response = json.loads(http_response.data)
    return response