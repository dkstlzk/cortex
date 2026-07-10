from typing import List
from backend.app.retrieval.models import QueryType, Chunk

# From Chapter 9 Table 9.5
FUSION_WEIGHTS = {
    QueryType.FACTUAL: {"graph": 0.2, "vector": 0.5, "lexical": 0.8},
    QueryType.DIAGNOSTIC: {"graph": 0.8, "vector": 0.5, "lexical": 0.2},
    QueryType.PROCEDURAL: {"graph": 0.8, "vector": 0.8, "lexical": 0.2},
    QueryType.OPEN: {"graph": 0.2, "vector": 0.8, "lexical": 0.5},
}

def fuse(
    graph_hits: List[Chunk], vector_hits: List[Chunk], lexical_hits: List[Chunk], weights: dict
) -> List[Chunk]:
    # Normalise scores per pathway, then apply weights, then dedup by chunk_id
    combined = {}
    
    for hits, source, weight in [(graph_hits, "graph", weights["graph"]),
                                 (vector_hits, "vector", weights["vector"]),
                                 (lexical_hits, "lexical", weights["lexical"])]:
        if not hits: continue
        min_score = min(h.score for h in hits)
        max_score = max(h.score for h in hits)
        
        for hit in hits:
            # Min-Max Normalization
            norm_score = hit.score if max_score == min_score else (hit.score - min_score) / (max_score - min_score)
            scored_val = norm_score * weight
            
            if hit.chunk_id not in combined or combined[hit.chunk_id].score < scored_val:
                hit.score = scored_val
                combined[hit.chunk_id] = hit
                
    # Return sorted combined hits
    return sorted(list(combined.values()), key=lambda x: -x.score)

def rerank(query: str, fused: List[Chunk]) -> List[Chunk]:
    # Local cross-encoder reranking mock
    # E.g., model = CrossEncoder('BAAI/bge-reranker-base')
    # scores = model.predict([(query, chunk.text) for chunk in fused])
    # For now, just return the top 8
    return fused[:8]
