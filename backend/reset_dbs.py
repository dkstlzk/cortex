
import os
import sys

# Ensure backend can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.shared.config import settings
from backend.shared.database import engine, Base
from backend.shared.redis_client import redis_conn
from backend.shared.neo4j_client import neo4j_driver
from backend.shared.qdrant_client import qdrant_client
from qdrant_client.http.models import Distance, VectorParams
from backend.shared.models.document import Document  # noqa: F401


def reset_postgres():
    print("Resetting PostgreSQL database...")
    # Drop all tables and recreate them
    Base.metadata.drop_all(bind=engine)
    print("Dropped PostgreSQL tables.")
    Base.metadata.create_all(bind=engine)
    print("Recreated PostgreSQL tables.")

from rq import Queue

def reset_redis():
    print("Flushing Redis and clearing queues...")
    try:
        # Explicitly empty the queue so workers stop grabbing jobs
        q = Queue('ingestion_queue', connection=redis_conn)
        q.empty()
        
        # Clear RQ registries (failed, started, etc)
        from rq.registry import FailedJobRegistry, StartedJobRegistry
        FailedJobRegistry(queue=q).cleanup()
        StartedJobRegistry(queue=q).cleanup()
    except Exception as e:
        print(f"Queue cleanup error: {e}")
        
    redis_conn.flushall()
    print("Redis flushed successfully.")

def reset_neo4j():
    print("Resetting Neo4j graph...")
    def _delete_all(tx):
        tx.run("MATCH (n) DETACH DELETE n")
    
    with neo4j_driver.session() as session:
        session.execute_write(_delete_all)
    print("Neo4j graph cleared.")

def reset_qdrant():
    print("Resetting Qdrant collection...")
    try:
        qdrant_client.delete_collection(collection_name=settings.QDRANT_COLLECTION)
        print(f"Deleted Qdrant collection: {settings.QDRANT_COLLECTION}")
    except Exception as e:
        print(f"Collection {settings.QDRANT_COLLECTION} may not exist: {e}")
        
    print(f"Creating Qdrant collection: {settings.QDRANT_COLLECTION}...")
    qdrant_client.create_collection(
        collection_name=settings.QDRANT_COLLECTION,
        vectors_config=VectorParams(size=settings.EMBEDDING_DIMENSION, distance=Distance.COSINE),
    )
    print("Qdrant collection created.")

def reset_storage():
    print("Resetting local artifact storage...")
    import shutil
    upload_dir = settings.UPLOAD_DIR
    if upload_dir.exists():
        shutil.rmtree(upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    print("Local artifact storage cleared.")

if __name__ == "__main__":
    print("Starting full database reset...")
    reset_redis()
    reset_neo4j()
    reset_qdrant()
    reset_storage()
    # Postgres is reset last
    reset_postgres()
    print("All databases and storage have been successfully cleared and initialized!")
