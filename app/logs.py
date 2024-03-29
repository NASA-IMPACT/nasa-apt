"""
Provides logging functionality for the APT API
- TODO: implement the use of this logging class throughout the API, instead
        of relying on a mixture of `logs.info()` and `print()` statements
"""
import logging

from app.config import APT_DEBUG

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)

if APT_DEBUG:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)
