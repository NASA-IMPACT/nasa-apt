"""
Collects various config values that are needed by the API. Most of these a
allow the API to contact other resources (database, elasticsearch, etc) and
are set by the CDK stack at deployment.
"""
import json
import os

import boto3

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


JWT_SECRET_ARN = os.environ.get("JWT_SECRET_ARN") or exit(
    "JWT_SECRET_ARN env var required"
)

POSTGRES_ADMIN_CREDENTIALS_ARN = os.environ.get(
    "POSTGRES_ADMIN_CREDENTIALS_ARN"
) or exit("POSTGRES_ADMIN_CREDENTIALS_ARN env var required")


ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL") or exit(
    "ELASTICSEARCH_URL env var required"
)

HOST = os.environ.get("FASTAPI_HOST") or exit("FASTAPI_HOST env var required")

IDP_METADATA_URL = os.environ.get("IDP_METADATA_URL") or exit(
    "IDP_METADATA_URL env var required"
)

S3_BUCKET = os.environ.get("S3_BUCKET") or exit("S3_BUCKET env var required")

AWS_RESOURCES_ENDPOINT = os.environ.get("AWS_RESOURCES_ENDPOINT")

secrets_manager_client_params = dict(service_name="secretsmanager")

# Allows us to point the APP to the AWS secretsmanager instance
# running in localstack, when developing locally. This value
# should be left blank when the APP is deployed in an AWS stack
if AWS_RESOURCES_ENDPOINT:
    secrets_manager_client_params.update(
        dict(endpoint_url=os.environ.get("AWS_RESOURCES_ENDPOINT"))
    )

secrets_manager = boto3.client(**secrets_manager_client_params)

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

JWT_SECRET = secrets_manager.get_secret_value(SecretId=JWT_SECRET_ARN)["SecretString"]
