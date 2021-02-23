"""STACK Configs."""

import os

PROJECT_NAME = "nasa-apt"
STAGE = os.environ.get("STAGE", "dev")

# Additional environement variable to set in the task/lambda
TASK_ENV: dict = dict()

VPC_ID = os.environ.get("VPC_ID")


################################################################################
#                                                                              #
#                                 LAMBDA                                       #
#                                                                              #
################################################################################
TIMEOUT: int = 10
MEMORY: int = 1536

# stack skips setting concurrency if this value is 0
# the stack will instead use unreserved lambda concurrency
MAX_CONCURRENT: int = 500 if STAGE == "prod" else 0

