import hashlib
import uuid
from pathlib import Path
import structlog
from fastapi import UploadFile

from backend.shared.config import settings

logger = structlog.get_logger(__name__)

class StorageManager:
    """
    Manages local filesystem operations for the CORTEX backend.
    """
    
    def __init__(self):
        self.upload_dir = settings.UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
    async def save_file(self, file: UploadFile, document_id: uuid.UUID) -> str:
        """
        Saves the uploaded file to disk using the document_id as the filename.
        Returns the absolute stored path.
        """
        extension = Path(file.filename or "").suffix
        if not extension:
            extension = ".pdf"
            
        stored_filename = f"{document_id}{extension}"
        stored_path = self.upload_dir / stored_filename
        
        # Reset file pointer before reading
        await file.seek(0)
        
        with stored_path.open("wb") as buffer:
            # Read in chunks to avoid memory issues with large files
            while chunk := await file.read(8192):
                buffer.write(chunk)
                
        logger.info("File saved to disk", stored_path=str(stored_path))
        return str(stored_path)
        
    async def calculate_sha256(self, file: UploadFile) -> str:
        """
        Calculates the SHA256 hash of the uploaded file.
        """
        sha256_hash = hashlib.sha256()
        
        # Reset file pointer before reading
        await file.seek(0)
        
        while chunk := await file.read(8192):
            sha256_hash.update(chunk)
            
        # Reset file pointer again for subsequent operations
        await file.seek(0)
        
        return sha256_hash.hexdigest()

storage_manager = StorageManager()
