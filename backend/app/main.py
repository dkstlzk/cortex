from fastapi import FastAPI
from app.api import query

app = FastAPI(title="CORTEX Fabric API")

app.include_router(query.router, prefix="/api", tags=["query"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
