# Cortex Submission Checklist

## Backend
- [ ] Ensure `uv run python -c "from backend.fabric_api.main import app"` executes without errors.
- [ ] Connect `kg/shared_tools.py` to the new `GraphRetriever` instead of the deleted `pathways.py`.
- [ ] Restore real entity resolution in `ContextAssembler` (query `pg_resolve_entities` instead of mocking).
- [ ] Restore real conversational history in `ContextAssembler`.
- [ ] Handle `KeywordRetriever` (either add the PostgreSQL migration for `fts` or explicitly disable/bypass the retriever).
- [ ] Ensure `app/api/graph.py` is present or the frontend graph endpoint is gracefully handled.

## Frontend
- [ ] Ensure `npm run build` succeeds (Verified: Yes).
- [ ] Ensure frontend can successfully connect to backend without CORS errors.
- [ ] Verify Graph Explorer does not crash if the backend `/api/v1/graph` returns a 404 or fails.

## Database
- [ ] PostgreSQL: Ensure `chunks` table exists.
- [ ] Neo4j: Ensure constraints/indexes are applied.
- [ ] Qdrant: Ensure `cortex_chunks` collection is initialized.

## Deployment
- [ ] Ensure `scripts/render-build.sh` runs successfully.
- [ ] Ensure `scripts/render-start.sh` executes staggered worker/API startup correctly.
- [ ] Set all environment variables (Neo4j URI, Postgres URI, Qdrant URL, OpenAI Keys).

## Testing
- [ ] Fix `tests/test_retrieval.py` to test the new `DefaultRetrievalPipeline`.
- [ ] Ensure `uv run pytest` collects and passes all tests.

## Smoke Tests
- [ ] Document upload succeeds and job is queued.
- [ ] Pipeline extracts chunks and pushes to Qdrant.
- [ ] Agent can answer a diagnostic question using Graph + Vector retrieval.
