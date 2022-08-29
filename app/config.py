"""
Collects various config values that are needed by the API. Most of these a
allow the API to contact other resources (database, elasticsearch, etc) and
are set by the CDK stack at deployment.
"""
import json
import os

import boto3

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
API_VERSION_STRING = os.environ.get("API_VERSION_STRING") or exit(
    "API_VERSION_STRING env var required"
)
PROJECT_NAME = os.environ.get("PROJECT_NAME") or exit("PROJECT_NAME env var required")
FRONTEND_URL = os.environ.get("APT_FRONTEND_URL") or exit(
    "APT_FRONTEND_URL env var required"
)

BACKEND_CORS_ORIGINS = os.environ.get(
    "BACKEND_CORS_ORIGINS",
    default=f"*,http://localhost:9000,http://localhost:3006,{FRONTEND_URL}",
)


POSTGRES_ADMIN_CREDENTIALS_ARN = os.environ.get(
    "POSTGRES_ADMIN_CREDENTIALS_ARN"
) or exit("POSTGRES_ADMIN_CREDENTIALS_ARN env var required")


ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL") or exit(
    "ELASTICSEARCH_URL env var required"
)


S3_BUCKET = os.environ.get("S3_BUCKET") or exit("S3_BUCKET env var required")


AWS_RESOURCES_ENDPOINT = os.environ.get("AWS_RESOURCES_ENDPOINT")

cognito = boto3.client("cognito-idp")
secrets_manager = boto3.client("secretsmanager")


# Allows us to point the APP to the AWS secretsmanager and cognito instances
# running in localstack, when developing locally. This value
# should be left blank when the APP is deployed in an AWS stack
if AWS_RESOURCES_ENDPOINT:
    secrets_manager = boto3.client(
        "secretsmanager", endpoint_url=AWS_RESOURCES_ENDPOINT
    )
    cognito = boto3.client("cognito-idp", endpoint_url=AWS_RESOURCES_ENDPOINT)


pg_credentials = json.loads(
    secrets_manager.get_secret_value(SecretId=POSTGRES_ADMIN_CREDENTIALS_ARN)[
        "SecretString"
    ]
)

POSTGRES_ADMIN_USER = pg_credentials["username"]
POSTGRES_ADMIN_PASSWORD = pg_credentials["password"]
POSTGRES_PORT = pg_credentials["port"]
POSTGRES_DB_NAME = pg_credentials["dbname"]
POSTGRES_HOST = pg_credentials["host"]

USER_POOL_NAME = os.environ.get("USER_POOL_NAME") or exit(
    "USER_POOL_NAME env var required"
)
APP_CLIENT_NAME = os.environ.get("APP_CLIENT_NAME") or exit(
    "APP_CLIENT_NAME env var required"
)


[USER_POOL_ID] = [
    x["Id"]
    for x in cognito.list_user_pools(MaxResults=60)["UserPools"]
    if x["Name"] == USER_POOL_NAME
]

[APP_CLIENT_ID] = [
    x["ClientId"]
    for x in cognito.list_user_pool_clients(MaxResults=60, UserPoolId=USER_POOL_ID)[
        "UserPoolClients"
    ]
    if x["ClientName"] == APP_CLIENT_NAME
]

COGNITO_KEYS_URL = f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"

if AWS_RESOURCES_ENDPOINT:
    COGNITO_KEYS_URL = f"{AWS_RESOURCES_ENDPOINT}/{USER_POOL_ID}/.well-known/jwks.json"


NOTIFICATIONS_FROM = os.environ.get("NOTIFICATIONS_FROM") or exit(
    "NOTIFICATIONS_FROM env var required"
)
