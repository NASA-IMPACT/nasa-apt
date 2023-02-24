"""Utility functions"""

from app import config


def get_task_queue():
    """Returns the SQS queue for background tasks"""
    if hasattr(config, "TASK_QUEUE_NAME"):
        return config.sqs.get_queue_by_name(QueueName=config.TASK_QUEUE_NAME)
    else:
        return config.sqs.Queue(config.TASK_QUEUE_URL)
