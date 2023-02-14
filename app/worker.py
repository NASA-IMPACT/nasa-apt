import pickle
import base64

from app.logs import logger
from app import config
from app.pdf.utils import make_pdf


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
        task_queue = config.sqs.get_queue_by_name(QueueName=config.TASK_QUEUE_NAME)
        messages = task_queue.receive_messages(MaxNumberOfMessages=1, WaitTimeSeconds=20)
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
