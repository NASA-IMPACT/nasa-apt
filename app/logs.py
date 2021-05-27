"""
Provides logging functionality for the APT API
- TODO: implement the use of this logging class throughout the API, instead
        of relying on a mixture of `logs.info()` and `print()` statements
"""
import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)
