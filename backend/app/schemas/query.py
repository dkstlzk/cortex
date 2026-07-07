from pydantic import BaseModel
from typing import Optional

class QueryRequest(BaseModel):
    query: str
    session_id: str
    focused_tag: Optional[str] = None

class TokenEventData(BaseModel):
    text: str

class CitationEventData(BaseModel):
    doc_id: str
    passage_id: str
    page: Optional[int] = None

class AgentTriggerEventData(BaseModel):
    worker: str
    job_id: str

class DoneEventData(BaseModel):
    answer_id: str
