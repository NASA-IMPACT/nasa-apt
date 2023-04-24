"""Utility functions"""

from functools import wraps

from app import config


def get_task_queue():
    """Returns the SQS queue for background tasks"""
    if hasattr(config, "TASK_QUEUE_NAME"):
        return config.sqs.get_queue_by_name(QueueName=config.TASK_QUEUE_NAME)
    else:
        return config.sqs.Queue(config.TASK_QUEUE_URL)


def run_once(f):
    """
    # From https://stackoverflow.com/a/4104188/3436502
    Runs a function (successfully) only once.
    The running can be reset by setting the `has_run` attribute to False
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        if not getattr(wrapper, "has_run", False):
            result = f(*args, **kwargs)
            setattr(wrapper, "has_run", True)
            return result

    setattr(wrapper, "has_run", False)
    return wrapper
