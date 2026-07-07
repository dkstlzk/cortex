from pydantic import BaseModel
from typing import Optional, Dict, Any

class AgentRequest(BaseModel):
    query: str
    session_id: str
    context: Optional[Dict[str, Any]] = None
