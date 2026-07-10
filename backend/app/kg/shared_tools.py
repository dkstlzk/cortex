from typing import Optional, List, Any
from backend.app.retrieval.models import QueryType, Chunk, GraphContext
from backend.app.retrieval.pathways import graph_pathway
from backend.app.retrieval.context import classify_query

# Knowledge graph retrieval tool exposed to P3.
async def context_graph_query(
    tag: str, query: str, depth: str = "auto", include_analogues: bool = False
) -> GraphContext:
    """
    Enhanced graph query tool for agents.
    
    'shallow': fixed-depth traversal only, max_depth=2 (fast, ~100ms)
    'deep': full five-phase context-aware pipeline, max_depth=5 (~300-500ms)
    'auto': shallow for Asset (history mode)/Comply, deep for Diagnose.
    """
    
    q_type = await classify_query(query)
    
    if depth == "auto":
        depth = "deep" if q_type == QueryType.DIAGNOSTIC else "shallow"
    
    passages = await graph_pathway(
        query=query, 
        query_type=q_type, 
        session_id="agent_session", 
        focused_tag=tag, 
        depth_mode=depth
    )
    
    return GraphContext(passages=passages)
