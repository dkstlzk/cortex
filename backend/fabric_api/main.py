from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from backend.shared.config import settings
from backend.shared.exceptions import CortexError
from backend.fabric_api.lifespan import lifespan
from backend.fabric_api.middleware import StructlogRequestMiddleware
from backend.fabric_api.exception_handlers import cortex_error_handler, generic_exception_handler
from backend.fabric_api.routes import health, upload
from backend.shared.constants import API_V1_PREFIX

logger = structlog.get_logger(__name__)

def create_app() -> FastAPI:
    """
    Application factory for the CORTEX Fabric API.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
    )

    # Register Middleware
    app.add_middleware(StructlogRequestMiddleware)
    # CORS is env-driven via CORS_ALLOW_ORIGINS (comma-separated, or "*").
    # The API authenticates with bearer tokens (Authorization header), not
    # cookies, so credentials are not required — which lets a wildcard origin
    # stay spec-valid (ACA-Origin: "*" is illegal alongside credentials).
    cors_origins = settings.cors_origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials="*" not in cors_origins,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Exception Handlers
    app.add_exception_handler(CortexError, cortex_error_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    app.include_router(health.router, prefix=API_V1_PREFIX)
    app.include_router(upload.router, prefix=API_V1_PREFIX)
    
    # Include P2/P3 application routers
    from backend.app.api import query, agents, graph
    app.include_router(query.router, prefix=API_V1_PREFIX, tags=["query"])
    app.include_router(agents.router, prefix=f"{API_V1_PREFIX}/agents", tags=["agents"])
    app.include_router(graph.router, prefix=API_V1_PREFIX, tags=["graph"])

    return app

# The ASGI application instance
app = create_app()
