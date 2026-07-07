import uuid
from fastapi import UploadFile, HTTPException, Depends
from rq import Queue
import structlog

from backend.shared.storage import StorageManager, storage_manager
from backend.shared.repositories.document_repository import DocumentRepository, get_document_repository
from backend.shared.redis_client import get_queue

logger = structlog.get_logger(__name__)

# Constants
ALLOWED_MIME_TYPES = ["application/pdf"]
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

class UploadService:
    """
    Orchestrates the document upload lifecycle: validation, storage, DB insertion, and enqueueing.
    """
    
    def __init__(self, repo: DocumentRepository, storage: StorageManager, queue: Queue):
        self.repo = repo
        self.storage = storage
        self.queue = queue

    async def process_upload(self, file: UploadFile) -> tuple[uuid.UUID, str, str]:
        """
        Processes an uploaded file.
        Returns a tuple of (document_id, job_id, status).
        """
        # 1. Validate MIME type
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=415, detail="Unsupported media type. Only PDF is allowed.")
            
        # 2. Validate File Size
        file.file.seek(0, 2)
        size_bytes = file.file.tell()
        file.file.seek(0)
        
        if size_bytes > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"Payload too large. Max size is {MAX_FILE_SIZE} bytes.")
            
        if size_bytes == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded.")
            
        # 3. Calculate SHA256
        sha256 = await self.storage.calculate_sha256(file)
        
        # Check for duplicates
        existing_doc = self.repo.get_by_sha256(sha256)
        if existing_doc:
            raise HTTPException(status_code=409, detail=f"Document with SHA256 {sha256} already exists.")
            
        # 4. Generate UUID
        document_id = uuid.uuid4()
        
        # 5. Save file
        stored_path = await self.storage.save_file(file, document_id)
        
        # 6. Insert Postgres
        document = self.repo.create(
            id=document_id,
            filename=file.filename or "unknown.pdf",
            stored_filename=f"{document_id}.pdf",
            mime_type=file.content_type,
            size_bytes=size_bytes,
            sha256=sha256,
            status="QUEUED"
        )
        
        # 7. Enqueue Redis Job
        job = self.queue.enqueue(
            "backend.ingestion_worker.jobs.process_document_job",
            kwargs={
                "document_id": str(document_id),
                "stored_path": stored_path
            },
            job_id=f"ingest_{document_id}",
            result_ttl=86400 # Keep result for 24h
        )
        logger.info("Enqueued ingestion job", document_id=str(document_id), job_id=job.id)
        
        return document.id, job.id, document.status

def get_upload_service(
    repo: DocumentRepository = Depends(get_document_repository),
    queue: Queue = Depends(get_queue)
) -> UploadService:
    """
    Dependency provider for UploadService.
    StorageManager is used as a singleton module.
    """
    return UploadService(repo, storage_manager, queue)
