import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.WARN)

logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)
