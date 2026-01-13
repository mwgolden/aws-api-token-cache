import os
import pytest

@pytest.fixture(scope="session", autouse=True)
def aws_creds():
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"


from moto import mock_aws
import boto3

@pytest.fixture(scope="session")
def mock_ssm():
    with mock_aws():
        ssm = boto3.client("ssm")
        ssm.put_parameter(
            Name="test_api_client_id",
            Description="client id",
            Value="TestAPIClient",
            Type="String"
        )

        ssm.put_parameter(
            Name="test_api_client_secret",
            Description="client secret",
            Value="ItsASecret!",
            Type="SecureString"
        )

        yield ssm