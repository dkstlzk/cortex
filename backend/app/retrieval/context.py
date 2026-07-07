from typing import List, Optional
from app.retrieval.models import TraversalContext, QueryType

# Mock dependencies
async def mock_resolve_entities(text: str) -> List[str]:
    # Extremely simple mock: just find known tags for Day 0
    tags = []
    if "P-101A" in text:
        tags.append("P-101A")
    if "P-101B" in text:
        tags.append("P-101B")
    return tags

async def mock_get_recent_messages(session_id: str, limit: int = 5) -> List[str]:
    # Mock chat history
    return []

async def mock_classify_query(query: str) -> QueryType:
    query_lower = query.lower()
    if "why" in query_lower or "root cause" in query_lower or "keeps failing" in query_lower:
        return QueryType.DIAGNOSTIC
    if "how do i" in query_lower or "steps to" in query_lower:
        return QueryType.PROCEDURAL
    if "which" in query_lower or "compatible" in query_lower or "compare" in query_lower:
        # Compositional queries are treated as OPEN for retrieval purposes
        return QueryType.OPEN
    if "what" in query_lower or "when" in query_lower:
        return QueryType.FACTUAL
    return QueryType.OPEN

async def mock_embed(text: str) -> List[float]:
    # Mock embedding: just return a zero vector
    return [0.0] * 384

async def assemble_context(
    query: str, session_id: str, focused_tag: Optional[str] = None
) -> TraversalContext:
    explicit = await mock_resolve_entities(query)
    
    history_texts = await mock_get_recent_messages(session_id, limit=5)
    history_tags = set()
    for msg in history_texts:
        history_tags.update(await mock_resolve_entities(msg))
        
    implicit = list(history_tags - set(explicit))
    if focused_tag and focused_tag not in explicit:
        implicit.insert(0, focused_tag)
        
    return TraversalContext(
        explicit_tags=explicit,
        implicit_tags=implicit[:5],  # Cap to prevent context explosion
        query_type=await mock_classify_query(query),
        query_embedding=await mock_embed(query)
    )
