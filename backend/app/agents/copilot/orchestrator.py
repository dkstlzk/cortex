"""
Copilot orchestrator — the main entry point for general query processing.

Implements the runtime flow:
    retrieve() → LLM Generation → Trigger Evaluation → stream or escalate

The Copilot never performs specialist reasoning. If escalation is required,
it constructs an EscalationContext and invokes the LangGraph workflow.
"""

from __future__ import annotations

import uuid
from typing import AsyncIterator, Optional

from backend.app.retrieval.models import QueryType
from backend.app.agents.shared.tools import retrieve, serialize_retrieval_context, serialize_citations
from backend.app.agents.shared.llm import generate_streaming
from backend.app.agents.shared.streaming import (
    emit_token,
    emit_citation,
    emit_done,
    emit_error,
)
from backend.app.agents.shared.state import EscalationContext
from backend.app.agents.shared.logging import get_logger, log_error
from backend.app.agents.copilot.prompts import build_copilot_messages
from backend.app.agents.copilot.classifier import evaluate_trigger
from backend.app.agents.graph.workflow import run_escalation_graph

logger = get_logger("copilot")


async def run_query(
    query: str,
    session_id: str,
    focused_tag: Optional[str] = None,
) -> AsyncIterator[str]:
    """
    Execute the full Copilot query lifecycle as an SSE event stream.

    This is the primary entry point that the API layer will call.
    It yields SSE-formatted strings suitable for a StreamingResponse.
    """
    answer_id = f"a-{uuid.uuid4().hex[:8]}"

    try:
        # --- Step 1: Retrieve context via P2 ---
        query_type = _classify_query_heuristic(query)
        retrieval_ctx = await retrieve(
            query=query,
            query_type=query_type,
            session_id=session_id,
            focused_tag=focused_tag,
        )

        # Group chunks by document, preserving the order of the highest-ranked chunk per document
        doc_groups = {}
        for chunk in retrieval_ctx.chunks:
            filename = chunk.payload.get("filename", "Unknown")
            if filename not in doc_groups:
                doc_groups[filename] = []
            doc_groups[filename].append(chunk)

        context_texts = []
        for filename, chunks in doc_groups.items():
            for chunk in chunks:
                page_numbers = chunk.payload.get("page_numbers", [])
                headings = chunk.payload.get("headings", [])
                chunk_idx = chunk.payload.get("chunk_index")
                
                header = f"Source: {filename}\n"
                if page_numbers:
                    header += f"Page: {page_numbers[0]}\n"
                if headings:
                    header += f"Section: {headings[-1]}\n"
                if chunk_idx is not None:
                    header += f"Chunk: {chunk_idx}\n"
                
                context_texts.append(f"{header}\n{chunk.text}")

        # --- Step 2: LLM Generation — stream tokens immediately ---
        messages = build_copilot_messages(query, context_texts)
        draft_parts: list[str] = []

        async for token_text in generate_streaming(messages):
            draft_parts.append(token_text)
            yield emit_token(token_text)

        draft_answer = "".join(draft_parts)

        # --- Step 3: Extract referenced citations ---
        import re
        referenced_citations = set()
        # Parse [Filename, ..., Chunk Y] format
        for match in re.finditer(r"\[\s*([^,\]]+?)\s*,(?:[^\]]*?)Chunk\s+(\d+)\s*\]", draft_answer, re.IGNORECASE):
            filename = match.group(1).strip()
            chunk_idx = int(match.group(2))
            referenced_citations.add((filename, chunk_idx))

        MAX_FALLBACK_CITATIONS = 4
        if not referenced_citations:
            logger.info(
                "citation_filter_fallback",
                reason="no_referenced_citations_found",
                retrieved=len(retrieval_ctx.citations),
                emitted=min(MAX_FALLBACK_CITATIONS, len(retrieval_ctx.citations)),
            )

        # --- Step 4: Emit citations from retrieval context ---
        emitted_count = 0
        for citation in retrieval_ctx.citations:
            if referenced_citations:
                if (citation.filename, citation.chunk_index) not in referenced_citations:
                    continue
            else:
                if emitted_count >= MAX_FALLBACK_CITATIONS:
                    continue
            
            emitted_count += 1
            yield emit_citation(
                doc_id=citation.doc_id,
                filename=citation.filename,
                passage_id=citation.passage_id,
                chunk_index=citation.chunk_index,
                page_numbers=citation.page_numbers,
                headings=citation.headings,
                page=citation.page,
            )

        # --- Step 4: Trigger Evaluation ---
        should_escalate, reason, confidence = await evaluate_trigger(
            query, draft_answer, session_id=session_id,
        )

        if not should_escalate:
            # Normal flow — done
            yield emit_done(answer_id)
            return

        # --- Step 5: Escalation via LangGraph ---
        escalation = EscalationContext(
            query=query,
            session_id=session_id,
            focused_tag=focused_tag,
            retrieval_context=serialize_retrieval_context(retrieval_ctx),
            citations=serialize_citations(retrieval_ctx),
            trigger_reason=reason,
            trigger_confidence=confidence,
            copilot_answer=draft_answer,
        )

        # LangGraph workflow: Supervisor → Worker
        async for event in run_escalation_graph(escalation):
            yield event

        yield emit_done(answer_id)

    except Exception as exc:
        log_error(logger, str(exc), session_id=session_id, exc_info=True)
        yield emit_error(str(exc))
        yield emit_done(answer_id)


def _classify_query_heuristic(query: str) -> QueryType:
    """
    Fast heuristic query classification used before retrieval.

    This mirrors the logic in backend/app/retrieval/context.py but is
    duplicated here intentionally: the Copilot needs a QueryType to call
    retrieve(), and importing classify_query from P2's context module
    would violate the P2→P3 boundary (it is internal to P2).
    """
    q = query.lower()
    if any(kw in q for kw in ("why", "keeps failing", "root cause")):
        return QueryType.DIAGNOSTIC
    if any(kw in q for kw in ("how do i", "steps to")):
        return QueryType.PROCEDURAL
    if any(kw in q for kw in ("which", "compatible", "compare")):
        return QueryType.OPEN
    if any(kw in q for kw in ("what", "when")):
        return QueryType.FACTUAL
    return QueryType.OPEN
