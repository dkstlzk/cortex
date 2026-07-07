from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter(tags=["Ingestion"])

class UploadResponse(BaseModel):
    detail: str

@router.post("/upload", response_model=UploadResponse, status_code=501)
async def upload_document(file: UploadFile = File(...)):
    """
    Contract for document upload.
    Will handle file persistence and queueing for ingestion in P1.3.
    """
    logger.info("Upload endpoint hit, returning 501 Not Implemented", filename=file.filename)
    
    return UploadResponse(detail="Ingestion pipeline not yet implemented.")
