from typing import List, Optional
import os
from openai import AsyncOpenAI
from backend.app.retrieval.models import TraversalContext, QueryType
from backend.app.db.queries import pg_facts, pg_resolve_entities, get_redis_session_history

FAST_MODEL_API_KEY = os.getenv("FAST_MODEL_API_KEY", "")
FAST_MODEL_BASE_URL = os.getenv("FAST_MODEL_BASE_URL")
EMBEDDING_MODEL_ENDPOINT = os.getenv("EMBEDDING_MODEL_ENDPOINT", "http://localhost:11434/v1")

# We use the standard OpenAI client since it can point to any compliant endpoint
openai_client = AsyncOpenAI(
    api_key=FAST_MODEL_API_KEY or "dummy",
    base_url=FAST_MODEL_BASE_URL
)
embed_client = AsyncOpenAI(api_key="dummy", base_url=EMBEDDING_MODEL_ENDPOINT)

async def resolve_entities(text: str) -> List[str]:
    return await pg_resolve_entities(text)

async def get_recent_messages(session_id: str, limit: int = 5) -> List[str]:
    return await get_redis_session_history(session_id, limit)

async def classify_query(query: str) -> QueryType:
    query_lower = query.lower()
    # Simple regex pre-filter as per architecture doc
    if any(m in query_lower for m in ["why", "keeps failing", "root cause"]):
        return QueryType.DIAGNOSTIC
    if any(m in query_lower for m in ["how do i", "steps to"]):
        return QueryType.PROCEDURAL
    if any(m in query_lower for m in ["which", "compatible", "compare"]):
        return QueryType.OPEN
    if any(m in query_lower for m in ["what", "when"]):
        return QueryType.FACTUAL
        
    # LLM fallback
    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Classify the query as one of: factual, diagnostic, procedural, open. Return only the single word."},
                {"role": "user", "content": query}
            ],
            max_tokens=10
        )
        cat = response.choices[0].message.content.strip().lower()
        if cat in [e.value for e in QueryType]:
            return QueryType(cat)
    except Exception:
        pass
    
    return QueryType.OPEN

async def embed(text: str) -> List[float]:
    # 1. Try the external API endpoint first
    try:
        if EMBEDDING_MODEL_ENDPOINT:
            response = await embed_client.embeddings.create(
                model="BAAI/bge-base-en-v1.5", # or any default
                input=[text]
            )
            return response.data[0].embedding
    except Exception:
        pass
        
    # 2. Fallback to local FastEmbed service
    try:
        from backend.shared.services.embedding_service import get_embedding_service
        service = get_embedding_service()
        vectors = service.embed_batch([text])
        return vectors[0]
    except Exception:
        from backend.shared.config import settings
        return [0.0] * settings.EMBEDDING_DIMENSION  # Fallback for local dev

async def assemble_context(
    query: str, session_id: str, focused_tag: Optional[str] = None
) -> TraversalContext:
    explicit = await resolve_entities(query)
    
    history_texts = await get_recent_messages(session_id, limit=5)
    history_tags = set()
    for msg in history_texts:
        history_tags.update(await resolve_entities(msg))
        
    implicit = list(history_tags - set(explicit))
    if focused_tag and focused_tag not in explicit:
        implicit.insert(0, focused_tag)
        
    return TraversalContext(
        explicit_tags=explicit,
        implicit_tags=implicit[:5],  # Cap to prevent context explosion
        query_type=await classify_query(query),
        query_embedding=await embed(query)
    )

