import asyncio
from typing import List, Optional

import structlog

from backend.app.retrieval.models import QueryType, Chunk, RetrievalContext
from backend.app.retrieval.context import classify_query
from backend.app.retrieval.pathways import graph_pathway, vector_pathway, lexical_pathway
from backend.app.retrieval.fusion import FUSION_WEIGHTS, fuse, rerank

logger = structlog.get_logger(__name__)


def _isolate(result, pathway: str) -> List[Chunk]:
    """Convert a gathered pathway result into a chunk list, absorbing failures.

    Each retrieval pathway is fault-isolated: a failure in one pathway (e.g. an
    unreachable store or a not-yet-populated table) degrades results rather than
    failing the whole query. Without this, one broken pathway would raise out of
    asyncio.gather and abort retrieval entirely.
    """
    if isinstance(result, Exception):
        logger.warning("retrieval_pathway_failed", pathway=pathway, error=str(result))
        return []
    return result


# Public retrieval interface consumed by P3.
async def retrieve(
    query: str, query_type: QueryType, session_id: str, focused_tag: Optional[str] = None
) -> RetrievalContext:

    # Run pathways in parallel, isolating each one's failures.
    graph_res, vector_res, lexical_res = await asyncio.gather(
        graph_pathway(query, query_type, session_id, focused_tag, depth_mode="deep"),
        vector_pathway(query),
        lexical_pathway(query),
        return_exceptions=True,
    )

    graph_hits = _isolate(graph_res, "graph")
    vector_hits = _isolate(vector_res, "vector")
    lexical_hits = _isolate(lexical_res, "lexical")

    fused = fuse(graph_hits, vector_hits, lexical_hits, weights=FUSION_WEIGHTS[query_type])
    chunks = rerank(query, fused)[:8]

    return RetrievalContext(
        chunks=chunks,
        metadata={"query_type": query_type.value}
    )

class CitedAnswer:
    def __init__(self, answer: str, citations: List[str]):
        self.answer = answer
        self.citations = citations

def citations_resolve(draft: str, chunks: List[Chunk]) -> bool:
    # Mock regex check for [doc_id:passage_id] tags
    return True

def prompt(query: str, chunks: List[Chunk], strict: bool = False) -> str:
    return "mock prompt"

def self_check(draft: str, chunks: List[Chunk]) -> CitedAnswer:
    return CitedAnswer(draft, ["d-91:p-4"])

async def generate_answer(query: str, chunks: List[Chunk]) -> CitedAnswer:
    # Mock LLM generation
    draft = "Pump P-101A has experienced a bearing failure. [d-91:p-4]"
    
    if not citations_resolve(draft, chunks):
        # Retry with strict citation instruction
        draft = "Strict: Pump P-101A has experienced a bearing failure. [d-91:p-4]"
        
    return self_check(draft, chunks)

# DEPRECATED/INTERNAL
# This function is NOT part of the frozen P2->P3 public contract.
# P3 should consume retrieve() instead.
async def retrieve_and_generate(query: str, session_id: str, focused_tag: Optional[str] = None) -> CitedAnswer:
    query_type = await classify_query(query)
    context = await retrieve(query, query_type, session_id, focused_tag)
    return await generate_answer(query, context.chunks)
