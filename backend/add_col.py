from sqlalchemy import text
from backend.shared.database import engine

with engine.begin() as conn:
    conn.execute(text("ALTER TABLE documents ADD COLUMN IF NOT EXISTS graph_job_status VARCHAR;"))
    print("Column added!")
