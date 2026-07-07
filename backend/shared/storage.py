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
        
    def save_and_hash_file(self, file: UploadFile, document_id: uuid.UUID) -> tuple[str, str]:
        """
        Saves the uploaded file to disk synchronously and computes its SHA256 hash in one pass.
        Returns a tuple of (stored_path, sha256_hash).
        """
        extension = Path(file.filename or "").suffix
        if not extension:
            extension = ".pdf"
            
        stored_filename = f"{document_id}{extension}"
        stored_path = self.upload_dir / stored_filename
        
        sha256_hash = hashlib.sha256()
        
        # Reset file pointer before reading
        file.file.seek(0)
        
        with stored_path.open("wb") as buffer:
            while chunk := file.file.read(8192):
                buffer.write(chunk)
                sha256_hash.update(chunk)
                
        logger.info("File saved to disk and hashed", stored_path=str(stored_path))
        return str(stored_path), sha256_hash.hexdigest()
        
    def delete_file(self, stored_path: str) -> None:
        """
        Deletes a file from disk if it exists. Used for cleanup on failure.
        """
        path = Path(stored_path)
        if path.exists() and path.is_file():
            path.unlink()
            logger.info("File deleted during cleanup", stored_path=stored_path)

storage_manager = StorageManager()
