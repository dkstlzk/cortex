from qdrant_client import AsyncQdrantClient
from neo4j import AsyncGraphDatabase
from psycopg_pool import AsyncConnectionPool
from backend.shared.config import settings

from backend.shared.config import settings

# All connection config comes from the single central settings object, so the
# async P2/P3 clients target exactly the same infrastructure as the sync
# ingestion workers (which read the same settings via shared/database.py).
QDRANT_URL = settings.QDRANT_URL
NEO4J_URI = settings.NEO4J_URI
NEO4J_USER = settings.NEO4J_USER
NEO4J_PASSWORD = settings.NEO4J_PASSWORD
DATABASE_URL = settings.postgres_dsn

qdrant_client = AsyncQdrantClient(url=QDRANT_URL)
neo4j_driver = AsyncGraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
pg_pool = AsyncConnectionPool(DATABASE_URL, open=False)

async def init_db_pools():
    await pg_pool.open()

async def close_db_pools():
    await pg_pool.close()
    await neo4j_driver.close()
    await qdrant_client.close()
