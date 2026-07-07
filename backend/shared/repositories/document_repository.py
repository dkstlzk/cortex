from fastapi import Depends
from sqlalchemy.orm import Session
import uuid
import structlog

from backend.shared.database import get_db
from backend.shared.models.document import Document

logger = structlog.get_logger(__name__)

class DocumentRepository:
    """
    Handles database operations for the Document model.
    """
    
    def __init__(self, db: Session):
        self.db = db

    def get_by_sha256(self, sha256: str) -> Document | None:
        """
        Retrieves a document by its SHA256 hash.
        """
        return self.db.query(Document).filter(Document.sha256 == sha256).first()

    def create(
        self, 
        id: uuid.UUID,
        filename: str, 
        stored_filename: str, 
        mime_type: str, 
        size_bytes: int, 
        sha256: str, 
        status: str
    ) -> Document:
        """
        Creates a new document record.
        """
        document = Document(
            id=id,
            filename=filename,
            stored_filename=stored_filename,
            mime_type=mime_type,
            size_bytes=size_bytes,
            sha256=sha256,
            status=status
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        logger.info("Document record created", document_id=str(document.id))
        return document

def get_document_repository(db: Session = Depends(get_db)) -> DocumentRepository:
    """
    Dependency provider for DocumentRepository.
    """
    return DocumentRepository(db)
