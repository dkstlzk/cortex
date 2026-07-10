from qdrant_client import AsyncQdrantClient
from neo4j import AsyncGraphDatabase
from psycopg_pool import AsyncConnectionPool
from backend.shared.config import settings

qdrant_client = AsyncQdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
neo4j_driver = AsyncGraphDatabase.driver(settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD))
pg_pool = AsyncConnectionPool(settings.database_url, open=False)

async def init_db_pools():
    await pg_pool.open()

async def close_db_pools():
    await pg_pool.close()
    await neo4j_driver.close()
    await qdrant_client.close()
