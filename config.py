# Application Configuration
import os
from app import app
# Base paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
DATABASE = os.path.join(BASE_DIR, 'database', 'pdf_index.db')
CHROMA_DB_PATH = os.path.join(BASE_DIR, 'database', 'chroma_db')

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
os.makedirs(CHROMA_DB_PATH, exist_ok=True)

# Flask config
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Search config
DEFAULT_SEARCH_TYPE = 'hybrid'  # keyword, semantic, hybrid
DEFAULT_RESULT_LIMIT = 20
CHUNK_SIZE = 500  # words per chunk
CHUNK_OVERLAP = 50  # overlap between chunks
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'