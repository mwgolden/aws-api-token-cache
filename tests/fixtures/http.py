import pytest
import urllib3
from unittest.mock import MagicMock

@pytest.fixture(scope="session")
def http_pool():
    return MagicMock(urllib3.PoolManager)