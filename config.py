# Application Configuration
# No circular imports - defines paths and settings only
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
UPLOAD_FOLDER = BASE_DIR / 'static' / 'uploads'
DATABASE = BASE_DIR / 'database' / 'pdf_index.db'
CHROMA_DB_PATH = BASE_DIR / 'database' / 'chroma_db'

# Create directories
UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
DATABASE.parent.mkdir(parents=True, exist_ok=True)
CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)

# Search config
DEFAULT_SEARCH_TYPE = 'hybrid'  # keyword, semantic, hybrid
DEFAULT_RESULT_LIMIT = 20
CHUNK_SIZE = 500  # words per chunk
CHUNK_OVERLAP = 50  # overlap between chunks
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'