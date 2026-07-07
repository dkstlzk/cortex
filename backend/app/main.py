from fastapi import FastAPI
from app.api import query, agents

app = FastAPI(title="CORTEX Fabric API")

app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
