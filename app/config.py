import os

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
POSTGRES_PORT = os.environ.get("POSTGRES_PORT", 5432)

POSTGRES_DB_NAME = os.environ.get("POSTGRES_DB_NAME") or exit(
    "POSTGRES_DB_NAME env var required"
)
POSTGRES_HOST = os.environ.get("POSTGRES_HOST") or exit(
    "POSTGRES_HOST env var required"
)
POSTGRES_ADMIN_USER = os.environ.get("POSTGRES_ADMIN_USER") or exit(
    "POSTGRES_ADMIN_USER env var required"
)
POSTGRES_ADMIN_PASSWORD = os.environ.get("POSTGRES_ADMIN_PASSWORD") or exit(
    "POSTGRES_ADMIN_PASSWORD env var required"
)

ELASTICURL = os.environ.get("ELASTICURL") or exit("ELASTICURL env var required")

ROOT_PATH = os.environ.get("API_PREFIX", "/")

JWT_SECRET = os.environ.get("JWT_SECRET") or exit("JWT_SECRET ENV var required")
HOST = os.environ.get("FASTAPI_HOST") or exit("FASTAPI_HOST env var required")

IDP_METADATA_URL = os.environ.get("IDP_METADATA_URL") or exit(
    "IDP_METADATA_URL env var required"
)

