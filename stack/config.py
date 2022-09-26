"""STACK Configs."""

import os

from dotenv import load_dotenv

load_dotenv()

################################################################################
#                                                                              #
#                           ENVIRONMENT CONFIG                                 #
#                                                                              #
################################################################################

PROJECT_NAME = os.environ.get("PROJECT_NAME", "nasa-apt-api")

# API_VERSION_STRING must start with `/`
API_VERSION_STRING = os.environ.get("API_VERSION_STRING", "/v1")

STAGE = os.environ.get("STAGE", "dev")
OWNER = os.environ.get("OWNER", "Development Seed - Byblos")
CLIENT = os.environ.get("CLIENT", "NASA Impact")
DEPLOY_DESTINATION = os.environ.get("DEPLOY_TO", "dev")


# Additional environement variable to set in the task/lambda
TASK_ENV: dict = dict()
VPC_ID = os.environ.get("VPC_ID")


################################################################################
#                                                                              #
#                                 LAMBDA                                       #
#                                                                              #
################################################################################
TIMEOUT: int = 60 * 2
MEMORY: int = 1536

# stack skips setting concurrency if this value is 0
# the stack will instead use unreserved lambda concurrency
MAX_CONCURRENT: int = 500 if STAGE == "prod" else 0


################################################################################
#                                                                              #
#                                 API CONFIG                                   #
#                                                                              #
################################################################################


FRONTEND_URL = os.environ.get("APT_FRONTEND_URL") or exit(
    "APT_FRONTEND_URL env var required"
)

# if STAGE != "prod":
#    FRONTEND_URL = f"{FRONTEND_URL},http://localhost:9000,https://nasa-apt.surge.sh"

BACKEND_CORS_ORIGINS = os.environ.get(
    "BACKEND_CORS_ORIGINS",
    # TODO: should this value be only `FRONTEND_URL`
    default=f"*,http://localhost:9000,http://localhost:3006,{FRONTEND_URL}",
)
# If using this value, ensure that the value is unique
# otherwise the deployment will fail
S3_BUCKET = os.environ.get("S3_BUCKET")

NOTIFICATIONS_FROM = os.environ.get("NOTIFICATIONS_FROM") or exit(
    "NOTIFICATIONS_FROM env var required"
)

GCC_MODE = bool(os.environ.get("GCC_MODE"))


################################################################################
#                                                                              #
#                          OPENSEARCH CONFIG                                   #
#                                                                              #
################################################################################

# Account/Service principal granted read/write access, based on current account

if not GCC_MODE:
    DEPLOY_DESTINATION = os.environ.get("DEPLOY_TO", "dev")
