"""
File utility functions
Handles file operations, validation, and path management
"""
import os
from pathlib import Path
from typing import Optional

# Setup logging
from services.log_config import get_logger
logger = get_logger(__name__)

# Base paths
BASE_DIR = Path(__file__).parent.parent
UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'


def ensure_directory(path: Path) -> None:
    """Ensure a directory exists"""
    path.mkdir(parents=True, exist_ok=True)


def get_upload_folder() -> Path:
    """Get the upload folder path"""
    ensure_directory(UPLOAD_FOLDER)
    return UPLOAD_FOLDER


def allowed_file(filename: str) -> bool:
    """Check if file is allowed (PDF only)"""
    return (
        '.' in filename and 
        filename.rsplit('.', 1)[1].lower() == 'pdf'
    )


def get_unique_filename(filename: str, folder: Optional[Path] = None) -> str:
    """
    Get a unique filename by appending counter if file exists
    
    Args:
        filename: Original filename
        folder: Target folder (defaults to UPLOAD_FOLDER)
    
    Returns:
        Unique filename that doesn't exist in the folder
    """
    if folder is None:
        folder = get_upload_folder()
    
    # Secure the filename first
    from werkzeug.utils import secure_filename
    filename = secure_filename(filename)
    
    base_name, ext = os.path.splitext(filename)
    filepath = folder / filename
    counter = 1
    
    while filepath.exists():
        filename = f"{base_name}_{counter}{ext}"
        filepath = folder / filename
        counter += 1
    
    return filename


def get_file_path(filename: str, folder: Optional[Path] = None) -> Path:
    """Get full file path"""
    if folder is None:
        folder = get_upload_folder()
    return folder / filename


def delete_file(filepath: str) -> bool:
    """Delete a file if it exists"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Deleted file: {filepath}")
            return True
    except Exception as e:
        logger.error(f"Error deleting file {filepath}: {e}")
    return False