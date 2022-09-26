"""AWS Lambda handler."""

# add logging support
from aws_lambda_powertools import Logger
from mangum import Mangum

from app.main import app

logger = Logger(service="mangum")

handler = Mangum(app)
