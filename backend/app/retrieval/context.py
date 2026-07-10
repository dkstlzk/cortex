from typing import List, Optional
from openai import AsyncOpenAI
from backend.app.retrieval.models import TraversalContext, QueryType
from backend.app.db.queries import pg_facts
from backend.shared.config import settings

# OpenAI-compatible client for the fast query classifier. Key, base URL, and
# model all come from the single central settings object so the P2 retrieval
# layer and the P3 agent layer target the exact same LLM endpoint.
openai_client = AsyncOpenAI(
    api_key=settings.fast_model_api_key or "dummy",
    max_retries=settings.LLM_MAX_RETRIES,
    timeout=settings.LLM_TIMEOUT,
    **({"base_url": settings.LLM_BASE_URL} if settings.LLM_BASE_URL else {}),
)

async def resolve_entities(text: str) -> List[str]:
    # Very naive mock of entity resolution.
    # In a real system, we would use an NER model or fuzzy match against entity_registry
    tags = []
    if "P-101A" in text:
        tags.append("P-101A")
    if "P-101B" in text:
        tags.append("P-101B")
    return tags

async def get_recent_messages(session_id: str, limit: int = 5) -> List[str]:
    # Mocking chat history fetch from DB for now
    return []

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
            model=settings.LLM_MODEL,
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

