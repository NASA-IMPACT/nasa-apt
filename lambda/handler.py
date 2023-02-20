"""AWS Lambda handler."""

from mangum import Mangum

from app.main import app
from app.worker import lambda_handler as tasks_handler  # noqa

handler = Mangum(app)
