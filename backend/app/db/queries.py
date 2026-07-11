from typing import Any, Dict, List, Tuple
from backend.shared.database import pg_pool
from backend.shared.neo4j_client import get_neo4j_async
from backend.shared.qdrant_client import get_qdrant_async

async def qdrant_search(query_embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
    # Assuming collection name is 'chunks'
    client = get_qdrant_async()
    response = await client.query_points(
        collection_name="cortex_chunks",
        query=query_embedding,
        limit=top_k
    )
    return [
        {
            "chunk_id": str(hit.id),
            "text": hit.payload.get("text", "") if hit.payload else "",
            "payload": hit.payload,
            "score": hit.score
        }
        for hit in response.points
    ]

async def neo4j_neighbors(tag: str) -> List[Tuple[str, str, float]]:
    query = """
    MATCH (start {tag: $tag})-[r]-(neighbor)
    RETURN neighbor.tag AS tag, type(r) AS rel_type, COALESCE(r.confidence, 1.0) AS confidence
    LIMIT 100
    """
    driver = get_neo4j_async()
    async with driver.session() as session:
        result = await session.run(query, tag=tag)
        records = await result.data()
        return [(rec["tag"], rec["rel_type"], rec["confidence"]) for rec in records]

async def pg_facts(doc_ids: List[str]) -> List[Dict[str, Any]]:
    if not doc_ids:
        return []
    query = "SELECT subject_tag, predicate, object_tag FROM facts WHERE source_doc_id = ANY(%s) AND status = 'active'"
    async with pg_pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute(query, (doc_ids,))
            rows = await cur.fetchall()
            return [
                {
                    "subject_tag": row[0],
                    "predicate": row[1],
                    "object_tag": row[2]
                }
                for row in rows
            ]

async def pg_resolve_entities(text: str) -> List[str]:
    """Resolve entities in text using ILIKE against entity_aliases."""
    if not text:
        return []
        
    query = "SELECT canonical_tag FROM entity_aliases WHERE %s ILIKE '%%' || alias || '%%'"
    
    try:
        async with pg_pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(query, (text,))
                rows = await cur.fetchall()
                return list(set(row[0] for row in rows))
    except Exception as e:
        # Fallback if table is missing or query fails
        import structlog
        logger = structlog.get_logger(__name__)
        logger.warning("Entity resolution query failed", error=str(e))
        return []

async def get_redis_session_history(session_id: str, limit: int = 5) -> List[str]:
    """Fetch recent message history from Redis."""
    from backend.shared.redis_client import redis_conn
    import asyncio
    key = f"session:{session_id}:history"
    try:
        messages = await asyncio.to_thread(redis_conn.lrange, key, -limit, -1)
        return [msg.decode('utf-8') for msg in messages if msg]
    except Exception:
        import structlog
        logger = structlog.get_logger(__name__)
        logger.warning(
            "Failed to fetch Redis session history",
            session_id=session_id,
            exc_info=True,
        )
        return []
