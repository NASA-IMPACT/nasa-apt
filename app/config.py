import os
import boto3
import json


PROJECT_NAME = "APT API"
# API_VERSION_STR = "/v1"
API_VERSION_STR = ""


FRONTEND_URL = os.environ.get("APT_FRONTEND_URL") or exit(
    "APT_FRONTEND_URL env var required"
)

BACKEND_CORS_ORIGINS = os.environ.get(
    "BACKEND_CORS_ORIGINS",
    default=f"*,http://localhost:3000,http://localhost:3006,{FRONTEND_URL}",
)

POSTGRES_ADMIN_CREDENTIALS_ARN = os.environ.get(
    "POSTGRES_ADMIN_CREDENTIALS_ARN"
) or exit("POSTGRES_ADMIN_CREDENTIALS_ARN env var required")

secrets_manager_client_params = dict(service_name="secretsmanager")

# Allows us to point the APP to the AWS secretsmanager instance
# running in localstack, when developing locally. This value
# should be left blank when the APP is deployed in an AWS stack
if os.environ.get("AWS_RESOURCES_ENDPOINT"):
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

ELASTICSEARCH_URL = os.environ.get("ELASTICSEARCH_URL") or exit(
    "ELASTICSEARCH_URL env var required"
)

JWT_SECRET = os.environ.get("JWT_SECRET") or exit("JWT_SECRET ENV var required")
HOST = os.environ.get("FASTAPI_HOST") or exit("FASTAPI_HOST env var required")

IDP_METADATA_URL = os.environ.get("IDP_METADATA_URL") or exit(
    "IDP_METADATA_URL env var required"
)

