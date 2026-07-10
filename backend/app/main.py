from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import query, agents

app = FastAPI(title="CORTEX Fabric API")

# Add CORS Middleware to prevent NetworkErrors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

app.include_router(query.router, prefix="/api", tags=["query"])
app.include_router(agents.router, prefix="/api/agents", tags=["agents"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}
