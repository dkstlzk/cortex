import asyncio
import json
from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.schemas.agent import AgentRequest

router = APIRouter()

async def mock_agent_sse(agent_type: str, request: AgentRequest):
    """
    Mock SSE stream for agent execution endpoints.
    Simulates the processing and response generation of an AI agent.
    """
    await asyncio.sleep(0.5)
    yield f"event: token\ndata: {json.dumps({'text': f'[{agent_type.capitalize()} Agent] Initializing for session {request.session_id}... '})}\n\n"
    
    await asyncio.sleep(0.5)
    yield f"event: token\ndata: {json.dumps({'text': f'Analyzing query: {request.query} '})}\n\n"
    
    await asyncio.sleep(0.5)
    yield f"event: done\ndata: {json.dumps({'answer_id': f'a-{agent_type}-123'})}\n\n"

@router.post("/asset")
async def agent_asset(request: AgentRequest):
    """
    Handle Asset Agent queries via SSE streaming.
    """
    return StreamingResponse(
        mock_agent_sse("asset", request),
        media_type="text/event-stream"
    )

@router.post("/diagnose")
async def agent_diagnose(request: AgentRequest):
    """
    Handle Diagnose Agent queries via SSE streaming.
    """
    return StreamingResponse(
        mock_agent_sse("diagnose", request),
        media_type="text/event-stream"
    )

@router.post("/comply")
async def agent_comply(request: AgentRequest):
    """
    Handle Comply Agent queries via SSE streaming.
    """
    return StreamingResponse(
        mock_agent_sse("comply", request),
        media_type="text/event-stream"
    )
