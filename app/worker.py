"""Worker for the background task queue

In development mode, the worker runs as a Python script in a separate container.
In production mode, the worker runs as a Lambda function attached to an SQS queue.

Currently, the only task is to generate PDFs. But in the future, we can add
other types of tasks as background tasks as required.
"""

import base64
import pickle

from app import config
from app.logs import logger
from app.pdf.utils import make_pdf
from app.utils import get_task_queue


def get_task_handlers():
    """Returns a dictionary of task handlers"""
    return {
        "make_pdf": make_pdf,
    }


def handle_task(task):
    """Handles a task"""
    task_type = task["task_type"]
    task_payload = task["payload"]
    handler = get_task_handlers()[task_type]
    handler(**task_payload)


def lambda_handler(event, context):
    """Lambda handler for the background task queue"""
    for record in event["Records"]:
        task = pickle.loads(base64.b64decode(record["body"].encode()))
        handle_task(task)


def worker():
    """Listens to an SQS queue for PDF generation requests"""
    while True:
        # get the next task
        task_queue = get_task_queue()
        messages = task_queue.receive_messages(
            MaxNumberOfMessages=1, WaitTimeSeconds=20
        )
        if not messages:
            continue

        message = messages[0]
        try:
            task = pickle.loads(base64.b64decode(message.body.encode()))
            logger.info(f"Handling task: {task}")
            handle_task(task)
        except Exception:
            logger.exception(f"Error handling task: {task}")
        finally:
            message.delete()


if __name__ == "__main__":
    logger.info("Starting the worker")
    worker()
