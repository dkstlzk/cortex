# Stabilization Roadmap for Cortex (10-Hour Budget)

This plan targets the highest-impact defects preventing Cortex from starting and executing retrieval pipelines correctly. The objective is to stabilize the system for demo and submission without introducing architectural scope creep.

## P0 — Must Fix Before Submission

### 1. Unblock Application Startup
**Problem**: The application currently crashes on `import backend.fabric_api.main` due to missing `pathways.py`.
**Why it matters**: Zero functionality is available. The backend cannot boot.
**Files**: `backend/app/kg/shared_tools.py`, `backend/tests/test_retrieval.py`
**Root cause**: A previous refactor deleted `pathways.py` but failed to update callers.
**Implementation strategy**:
- Modify `shared_tools.py` to stop importing `graph_pathway`. Instead, use the new `GraphRetriever` directly or isolate graph passages via `DefaultRetrievalPipeline`.
- Update `tests/test_retrieval.py` to target `RetrievalPipeline` and remove references to `citations_resolve`.
**Risk**: Low. This is just correctly wiring the existing architecture.
**Estimated effort**: 45 minutes.
**Dependencies**: None.
**Verification steps**: Run `uv run python -c "from backend.fabric_api.main import app"` and verify it returns a clean exit code (0).
**Regression risks**: None, since it currently crashes.

### 2. Restore Entity Resolution (Context Extraction)
**Problem**: The `ContextAssembler` is currently mocked, hardcoding "P-101A" as an entity and ignoring real database queries.
**Why it matters**: Graph seed extraction will fail for any query not involving exactly "P-101A".
**Files**: `backend/app/retrieval/context.py`, `backend/app/db/queries.py`
**Root cause**: The previous refactor stubbed out the database lookup for testing and never restored it.
**Implementation strategy**:
- Add `pg_resolve_entities(text: str)` to `queries.py` to query the `entity_aliases` table using ILIKE.
- Import `pg_resolve_entities` in `context.py` and replace the mocked logic in `resolve_entities()`.
**Risk**: Low to Medium (requires writing simple SQL).
**Estimated effort**: 1 hour.
**Dependencies**: Postgres connection pool.
**Verification steps**: Add a pytest asserting that `assemble_context("What is the status of Valve 99?")` successfully extracts `Valve 99`.
**Regression risks**: Potential latency increase for retrieval.

---

## P1 — Strongly Recommended Before Submission

### 3. Disable Lexical Retrieval (KeywordRetriever)
**Problem**: `KeywordRetriever` uses `fts @@ plainto_tsquery` on the `chunks` table, but the `fts` column does not exist in the schema.
**Why it matters**: Every retrieval query will experience a silent SQL exception under the hood, degrading performance and generating error logs.
**Files**: `backend/app/retrieval/orchestrator.py`
**Root cause**: No Alembic migration was written to support lexical search.
**Implementation strategy**:
- Rather than attempting to write a migration in the 11th hour, gracefully disable it: remove `KeywordRetriever()` from the list in `get_retrieval_pipeline()`.
**Risk**: Low.
**Estimated effort**: 5 minutes.
**Dependencies**: None.
**Verification steps**: Ensure full pipeline runs without SQL errors.
**Regression risks**: Loss of lexical capability (but it was already broken).

### 4. Restore Graph API Endpoint
**Problem**: `backend/app/api/graph.py` is missing.
**Why it matters**: The frontend Graph Explorer will encounter 404s and fail to render any topology.
**Files**: `backend/app/api/graph.py`, `backend/fabric_api/main.py`
**Root cause**: The file was seemingly deleted or moved during restructuring.
**Implementation strategy**:
- Recreate the `/api/v1/graph` router.
- Add a read-only endpoint that executes a simple Cypher query `MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 100` and formats it for React flow.
- Include the router in `fabric_api/main.py`.
**Risk**: Medium.
**Estimated effort**: 1.5 hours.
**Dependencies**: Neo4j driver.
**Verification steps**: Hit `GET /api/v1/graph` via curl and ensure nodes/edges are returned.
**Regression risks**: None.

---

## P2 — Safe To Defer

### 5. CORS and Authentication
**Problem**: Backend accepts all origins and has no JWT/auth verification.
**Why it matters**: Security vulnerability.
**Files**: `backend/fabric_api/main.py`
**Root cause**: Not implemented.
**Implementation strategy**: Accept the risk for the demo window, as this system is deployed on an isolated network for grading.
**Risk**: High in real prod, Low for this hackathon/submission.
**Estimated effort**: N/A.

### 6. Full CI/CD Pipeline
**Problem**: Lack of CI allowed the `ModuleNotFoundError` to ship.
**Why it matters**: Future changes will break things again.
**Implementation strategy**: Add a simple GitHub action to `uv run pytest` on PR.
**Estimated effort**: 30 minutes.
