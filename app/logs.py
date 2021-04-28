import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)
