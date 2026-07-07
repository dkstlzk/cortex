import structlog
from contextlib import asynccontextmanager
from fastapi import FastAPI

from backend.shared.config import settings
from backend.shared.logging import setup_logging
from backend.shared.database import engine
from backend.shared.neo4j_client import neo4j_driver
from backend.shared.qdrant_client import qdrant_client
from backend.shared.redis_client import redis_conn

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI lifespan context manager for graceful startup and shutdown.
    Replaces deprecated @app.on_event("startup") and @app.on_event("shutdown").
    """
    # Startup Sequence
    setup_logging()
    logger.info("Application starting up...", version=settings.VERSION)
    
    # Ensure UPLOAD_DIR exists
    try:
        settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("Upload directory verified", path=str(settings.UPLOAD_DIR))
    except Exception as e:
        logger.error("Failed to create upload directory", error=str(e))
        raise

    # Verification check
    neo4j_driver.verify_connectivity()
    redis_conn.ping()
    
    from backend.shared.services.qdrant_service import get_qdrant_service
    get_qdrant_service().bootstrap_collections()
    
    logger.info("Infrastructure clients verified and ready.")

    yield # Yield control to the FastAPI application

    # Shutdown Sequence
    logger.info("Application shutting down. Closing infrastructure connections...")
    
    try:
        neo4j_driver.close()
        logger.info("Neo4j driver closed.")
    except Exception as e:
        logger.error("Error closing Neo4j driver", error=str(e))
        
    try:
        redis_conn.close()
        logger.info("Redis connection closed.")
    except Exception as e:
        logger.error("Error closing Redis connection", error=str(e))
        
    try:
        engine.dispose()
        logger.info("PostgreSQL engine disposed.")
    except Exception as e:
        logger.error("Error disposing PostgreSQL engine", error=str(e))
        
    try:
        qdrant_client.close()
        logger.info("Qdrant client closed.")
    except Exception as e:
        logger.error("Error closing Qdrant client", error=str(e))

    logger.info("Shutdown sequence complete.")
