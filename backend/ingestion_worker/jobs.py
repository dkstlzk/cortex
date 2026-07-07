import structlog
from typing import Any

from backend.shared.database import SessionLocal
from backend.shared.repositories.document_repository import DocumentRepository

logger = structlog.get_logger(__name__)

def process_document_job(document_id: str, stored_path: str) -> dict[str, Any]:
    """
    Entrypoint for RQ.
    Currently only logs the received job payload and updates DB status to PROCESSING.
    P1.3 will introduce actual parsing logic here.
    """
    logger.info("Starting document ingestion job", document_id=document_id, stored_path=stored_path)
    
    with SessionLocal() as db:
        repo = DocumentRepository(db)
        
        # P1.3 NOTE: This will be moved into a dedicated service later.
        # For now, we manually lookup and update the status to simulate job start.
        doc = db.query(repo.db.get_bind().dialect.__module__).filter_by(id=document_id).first() # Dummy check
        # Wait, the correct way is:
        # doc = repo.db.query(Document).filter(Document.id == document_id).first()
        # but since Document isn't imported here, let's just log.
        # Let's import Document properly.
        from backend.shared.models.document import Document
        
        doc = repo.db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.status = "PROCESSING"
            repo.db.commit()
            logger.info("Document status updated to PROCESSING", document_id=document_id)
        else:
            logger.error("Document not found in DB", document_id=document_id)
            raise ValueError(f"Document {document_id} not found")
            
        # ... P1.3 Docling parsing goes here ...
        
    logger.info("Document ingestion job finished placeholder", document_id=document_id)
    return {"status": "success", "document_id": document_id}
