from functools import lru_cache
from backend.shared.services.embedding_service.provider import EmbeddingProvider
from backend.shared.services.embedding_service.fastembed_provider import FastEmbedProvider
from backend.shared.services.embedding_service.openai_provider import OpenAIEmbeddingProvider
from backend.shared.config import settings
import structlog

logger = structlog.get_logger(__name__)

@lru_cache(maxsize=1)
def get_embedding_service() -> EmbeddingProvider:
    """
    Dependency provider for the embedding service.
    Returns OpenAIEmbeddingProvider if a remote API endpoint is configured,
    otherwise falls back to the local FastEmbed provider.
    """
    if settings.EMBEDDING_MODEL_ENDPOINT and settings.EMBEDDING_MODEL_ENDPOINT != "http://localhost:11434/v1":
        logger.info("Using remote OpenAI-compatible API for embeddings", endpoint=settings.EMBEDDING_MODEL_ENDPOINT)
        return OpenAIEmbeddingProvider(
            endpoint=settings.EMBEDDING_MODEL_ENDPOINT,
            model_name=settings.EMBEDDING_MODEL
        )
        
    logger.info("Using local FastEmbed for embeddings", model=settings.EMBEDDING_MODEL)
    return FastEmbedProvider(model_name=settings.EMBEDDING_MODEL)
