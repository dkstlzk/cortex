from typing import List, Optional
import os
from openai import AsyncOpenAI
from backend.app.retrieval.models import TraversalContext, QueryType
from backend.app.db.queries import pg_facts, pg_resolve_entities, get_redis_session_history
from backend.shared.config import settings

FAST_MODEL_API_KEY = os.getenv("FAST_MODEL_API_KEY", "")
FAST_MODEL_BASE_URL = os.getenv("FAST_MODEL_BASE_URL") or None
EMBEDDING_MODEL_ENDPOINT = os.getenv("EMBEDDING_MODEL_ENDPOINT") or None

# We will dynamically instantiate clients based on available environment variables
# during the function calls to support robust cascading fallbacks.

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
        
    messages = [
        {"role": "system", "content": "Classify the query as one of: factual, diagnostic, procedural, open. Return only the single word."},
        {"role": "user", "content": query}
    ]
    
    # 1. Try Custom AMD GPU / vLLM Tunnel / Cloud Provider (Google, Fireworks, etc)
    # Only use this if the user actually specified a custom FAST_MODEL in .env!
    if settings.FAST_MODEL:
        try:
            # We pass the base URL if it exists, otherwise it tries to resolve it natively
            client = AsyncOpenAI(
                api_key=FAST_MODEL_API_KEY or "dummy", 
                **({"base_url": FAST_MODEL_BASE_URL} if FAST_MODEL_BASE_URL else {})
            )
            response = await client.chat.completions.create(
                model=settings.FAST_MODEL,
                messages=messages,
                max_tokens=10
            )
            cat = response.choices[0].message.content.strip().lower()
            if cat in [e.value for e in QueryType]:
                return QueryType(cat)
        except Exception:
            pass # Fall back to official
            
    # 2. Try Official OpenAI
    if FAST_MODEL_API_KEY and FAST_MODEL_API_KEY != "<replace_with_your_api_key>":
        try:
            client = AsyncOpenAI(api_key=FAST_MODEL_API_KEY)
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                max_tokens=10
            )
            cat = response.choices[0].message.content.strip().lower()
            if cat in [e.value for e in QueryType]:
                return QueryType(cat)
        except Exception:
            pass
    
    # 3. Default fallback
    return QueryType.OPEN

async def embed(text: str) -> List[float]:
    # 1. Try Custom AMD GPU or Cloud Provider
    if EMBEDDING_MODEL_ENDPOINT:
        try:
            client = AsyncOpenAI(api_key=FAST_MODEL_API_KEY or "dummy", base_url=EMBEDDING_MODEL_ENDPOINT)
            response = await client.embeddings.create(model=settings.EMBEDDING_MODEL, input=[text])
            return response.data[0].embedding
        except Exception:
            pass
            
    # 2. Try Official OpenAI
    if FAST_MODEL_API_KEY and FAST_MODEL_API_KEY != "<replace_with_your_api_key>":
        try:
            client = AsyncOpenAI(api_key=FAST_MODEL_API_KEY)
            response = await client.embeddings.create(model="text-embedding-3-small", input=[text])
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

