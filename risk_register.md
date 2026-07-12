| Risk | Likelihood | Impact | Mitigation | Owner | Priority |
| --- | --- | --- | --- | --- | --- |
| **Backend Startup Failure** | High | Critical | Fix the `graph_pathway` import in `kg/shared_tools.py` by mapping it to the new `GraphRetriever` or `RetrievalPipeline`. Add a startup CI check. | Backend Team | P0 |
| **Mocked Entity Resolution Failure** | High | High | Restore `pg_resolve_entities` in `ContextAssembler` to enable dynamic entity extraction, replacing the hardcoded "P-101A" mock. | Backend Team | P0 |
| **Lexical Retrieval SQL Crash** | High | Medium | Since `chunks` lacks an `fts` column, either skip `KeywordRetriever` during demo or add a quick Alembic migration. | DB Team | P1 |
| **Missing Graph API Endpoint** | Medium | High | Re-implement `app/api/graph.py` to serve the frontend's network topology view, or mock the response if time doesn't permit. | Backend Team | P1 |
| **Broken Test Suite** | High | Medium | Rewrite `test_retrieval.py` to use `RetrievalPipeline`. Fix `test_upload.py` by resolving the global import crashes. | QA / Backend | P2 |
| **No Authentication** | High | Low | Accept as a known limitation for the 10-hour stabilization window. | Security Team | P2 |
