from qdrant_client import QdrantClient
import structlog
from typing import Generator

from backend.shared.config import settings

logger = structlog.get_logger(__name__)

qdrant_client = QdrantClient(
    url=settings.QDRANT_URL,
    api_key=settings.QDRANT_API_KEY
)

def get_qdrant() -> Generator[QdrantClient, None, None]:
    """
    Dependency to get the Qdrant client.
    """
    yield qdrant_client
