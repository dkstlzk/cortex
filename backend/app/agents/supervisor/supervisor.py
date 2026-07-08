"""
Supervisor — receives an EscalationContext, routes to a worker,
and delegates execution.

This module ties routing to worker dispatch. The Supervisor itself
performs no retrieval, prompt construction, or LLM invocation.
"""

from __future__ import annotations

import uuid
from typing import AsyncIterator

from backend.app.agents.shared.state import (
    AgentState,
    EscalationContext,
    WorkerType,
)
from backend.app.agents.shared.logging import get_logger, log_worker_lifecycle
from backend.app.agents.shared.streaming import emit_agent_trigger
from backend.app.agents.supervisor.router import route
from backend.app.agents.asset.worker import run as run_asset
from backend.app.agents.diagnose.worker import run as run_diagnose
from backend.app.agents.comply.worker import run as run_comply

logger = get_logger("supervisor")

_WORKER_DISPATCH = {
    WorkerType.ASSET: run_asset,
    WorkerType.DIAGNOSE: run_diagnose,
    WorkerType.COMPLIANCE: run_comply,
}


async def route_escalation(escalation: EscalationContext) -> AsyncIterator[str]:
    """
    Route an escalated query to the appropriate specialist worker.

    Constructs the AgentState from the EscalationContext and dispatches
    to the selected worker. Yields SSE events from the worker directly
    into the caller's stream.
    """
    worker_type = await route(escalation)
    
    job_id = f"j-{uuid.uuid4().hex[:8]}"
    yield emit_agent_trigger(worker=worker_type.value, job_id=job_id)

    state = AgentState(
        query=escalation.query,
        session_id=escalation.session_id,
        thread_id=escalation.thread_id,
        focused_tag=escalation.focused_tag,
        worker=worker_type,
        retrieval_context=escalation.retrieval_context,
        citations=escalation.citations,
        conversation=escalation.conversation,
    )

    log_worker_lifecycle(
        logger, "started",
        worker=worker_type.value,
        session_id=escalation.session_id,
    )

    worker_fn = _WORKER_DISPATCH[worker_type]

    async for event in worker_fn(state):
        yield event

    log_worker_lifecycle(
        logger, "completed",
        worker=worker_type.value,
        session_id=escalation.session_id,
    )


async def run_worker_direct(state: AgentState) -> AsyncIterator[str]:
    """
    Execute a worker directly from an AgentState (for explicit endpoints).

    Used by POST /asset, POST /diagnose, POST /comply which bypass the
    Copilot and Supervisor and construct AgentState directly from AgentRequest.
    """
    if state.worker is None:
        raise ValueError("AgentState.worker must be set for direct worker execution")

    worker_fn = _WORKER_DISPATCH[state.worker]

    log_worker_lifecycle(
        logger, "started_direct",
        worker=state.worker.value,
        session_id=state.session_id,
    )

    async for event in worker_fn(state):
        yield event

    log_worker_lifecycle(
        logger, "completed_direct",
        worker=state.worker.value,
        session_id=state.session_id,
    )
