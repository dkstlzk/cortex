# Backend Hand-off Document for P3

This document summarizes the recently refactored and "frozen" API contracts, data models, and shared functions available for agent development.

## 1. Frozen API Endpoints

The system relies on Server-Sent Events (SSE) for streaming both general copilot queries and specific agent executions.

### General Query Endpoint
- **Route:** `POST /query`
- **File:** `backend/app/api/query.py`
- **Request Body:** `QueryRequest` (query, session_id, focused_tag)
- **Response:** `StreamingResponse` (text/event-stream)
- **Supported Events:** `token`, `citation`, `agent_trigger`, `done`, `reasoning`, `tool_call`, `tool_result`, `error`

### Agent Endpoints
- **Routes:** `POST /asset`, `POST /diagnose`, `POST /comply`
- **File:** `backend/app/api/agents.py`
- **Request Body:** `AgentRequest` (query, session_id, thread_id, focused_tag)
- **Response:** `StreamingResponse` (text/event-stream) 
- *Note:* Agents can also resolve their final answers to the `AgentResponse` schema if a structured payload is needed at the end of the stream.

---

## 2. Shared Data Models

> [!IMPORTANT]
> All primary models have been strongly typed using Pydantic and Dataclasses to ensure strict contracts across team boundaries.

**Agent Schemas (`backend/app/schemas/agent.py`)**
```python
class AgentRequest(BaseModel):
    query: str
    session_id: str
    thread_id: Optional[str] = None
    focused_tag: Optional[str] = None

class AgentResponse(BaseModel):
    answer: str
    citations: List[str] = []
    error: Optional[str] = None
```

**Retrieval Models (`backend/app/retrieval/models.py`)**
```python
@dataclass
class Citation:
    doc_id: str
    passage_id: str
    page: Optional[int] = None
    text_snippet: Optional[str] = None

@dataclass
class GraphContext:
    passages: List[Chunk]
    entities: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)

@dataclass
class RetrievalContext:
    chunks: List[Chunk]
    graph_context: Optional[GraphContext] = None
    citations: List[Citation] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

---

## 3. Shared Functions & Tooling

P3 should utilize the following shared orchestrator and graph tools when building out the agent workflows.

### Retrieval Orchestration
**File:** `backend/app/retrieval/orchestrator.py`
- `async def retrieve(query, query_type, session_id, focused_tag) -> RetrievalContext`
  - Runs graph, vector, and lexical pathways in parallel, fuses the results, and returns a structured `RetrievalContext`.
- `async def retrieve_and_generate(query, session_id, focused_tag) -> CitedAnswer`
  - Handles the end-to-end lifecycle: classifies the query, performs retrieval, and generates a checked answer.

### Knowledge Graph Agent Tools
**File:** `backend/app/kg/shared_tools.py`
- `async def context_graph_query(tag, query, depth="auto", include_analogues=False) -> GraphContext`
  - Intended to be exposed as an explicit tool for the Agents.
  - Dynamically runs the full context-aware graph pipeline (deep vs shallow) and returns the robust `GraphContext` dataclass.
