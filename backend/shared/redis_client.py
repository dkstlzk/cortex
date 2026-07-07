from redis import Redis
from rq import Queue
import structlog
from typing import Generator

from backend.shared.config import settings
from backend.shared.constants import INGESTION_QUEUE_NAME

logger = structlog.get_logger(__name__)

try:
    redis_conn = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=settings.REDIS_DB,
        decode_responses=False  # Keep false for RQ binary compatibility
    )
    redis_conn.ping()
    
    # Initialize the default RQ queue
    ingestion_queue = Queue(INGESTION_QUEUE_NAME, connection=redis_conn)
    
    logger.info("Redis connection and RQ queue initialized.")
except Exception as e:
    logger.error("Redis initialization failed", error=str(e))
    raise

def get_redis() -> Generator[Redis, None, None]:
    """
    Dependency to get the raw Redis connection.
    """
    yield redis_conn

def get_queue() -> Generator[Queue, None, None]:
    """
    Dependency to get the RQ ingestion queue.
    """
    yield ingestion_queue
