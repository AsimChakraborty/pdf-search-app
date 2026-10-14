# PDF Search Engine - AI Powered

A powerful web-based application for searching across multiple PDF documents using keyword, semantic (AI-powered), and hybrid search methods.

## Features

- **Multiple PDF Upload**: Upload 40+ PDFs simultaneously via drag-and-drop or file selection
- **Keyword Search**: Traditional full-text search using SQLite FTS5
- **Semantic Search**: AI-powered search using sentence embeddings to find conceptually similar content
- **Hybrid Search**: Combines keyword and semantic search for optimal results
- **Fast Performance**: Pre-indexed text enables sub-second search queries
- **Persistent Storage**: Data survives application restarts

## Use Case Example

User uploads 100 PDF documents
User searches: "business opportunity in Bangladesh"
System finds documents containing relevant information even when exact phrase doesn''t appear

## Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.12+ |
| Web Framework | Flask 3.x |
| PDF Processing | pdfplumber |
| Keyword Search | SQLite with FTS5 |
| Semantic Search | ChromaDB + Sentence Transformers |
| Embedding Model | all-MiniLM-L6-v2 |
| Frontend | HTML, CSS, JavaScript |

## Project Structure

```
scan_test/
+-- app.py                    # Main Flask application
+-- config.py                 # Application configuration
+-- requirements.txt          # Python dependencies
+-- pyproject.toml           # uv project config
�
+-- services/                # Business logic
�   +-- __init__.py         # Text extraction & chunking
�   +-- keyword_search.py   # SQLite FTS5 search
�   +-- semantic_search.py  # ChromaDB vector search
�   +-- hybrid_search.py    # Combined search
�   +-- embedding_service.py # Sentence embeddings
�
+-- database/               # Data storage
�   +-- pdf_index.db       # SQLite database
�   +-- chroma_db/         # ChromaDB vector store
�
+-- static/
�   +-- uploads/           # Uploaded PDF files
�
+-- templates/
�   +-- index.html         # Web UI
�
+-- scripts/
�   +-- migrate_pdfs.py    # Migration utility
�
+-- docs/                  # Documentation
�   +-- API.md
�   +-- ARCHITECTURE.md
�   +-- INSTALLATION.md
�   +-- TROUBLESHOOTING.md
�   +-- INDEX.md
�
+-- .venv/                 # Virtual environment
```

## Quick Start

### Prerequisites

- Python 3.12 or higher
- Windows 10/11

### Installation



1. Create virtual environment (if not exists):
```bash
uv venv --python 3.12
```

2. Install dependencies:
```bash
uv pip install flask pdfplumber werkzeug sentence-transformers chromadb numpy torch torchvision
```

Or use existing virtual environment:
```bash
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Running the Application

```bash
.venv\Scripts\python.exe app.py
```

Then open your browser to: http://127.0.0.1:5000

### Stopping the Server

Press Ctrl+C in the terminal.

## Search Types Explained

### 1. Keyword Search
- Uses SQLite FTS5 (Full-Text Search)
- Finds exact word/phrase matches
- Supports wildcards: Bangladesh*
- Results ranked by BM25 algorithm
- Best for: Exact matches, specific terms

### 2. Semantic Search
- Uses AI sentence embeddings (all-MiniLM-L6-v2)
- Finds conceptually similar content
- Works even when exact words don''t match
- Stores vectors in ChromaDB
- Best for: Finding related concepts, synonyms

### 3. Hybrid Search
- Combines keyword and semantic results
- Weighted scoring (50/50 default)
- Shows results that match both methods first
- Best for: Comprehensive search results

## API Documentation

### Core Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Home page (HTML UI) |
| POST | `/api/upload` | Upload PDF files |
| GET | `/api/search?q=query&type=type` | Search PDFs |
| GET | `/api/search/all?q=query` | Search all types |
| GET | `/api/pdfs` | List all PDFs |
| DELETE | `/api/pdf/<id>` | Delete a PDF |
| POST | `/api/reindex` | Rebuild ChromaDB index |

### Example API Usage

**Search:**
```bash
# Keyword search
GET /api/search?q=Bangladesh&type=keyword

# Semantic search
GET /api/search?q=business opportunity&type=semantic

# Hybrid search (default)
GET /api/search?q=business opportunity&type=hybrid

# Search all types
GET /api/search/all?q=business opportunity
```

**List PDFs:**
```bash
GET /api/pdfs
```

**Delete PDF:**
```bash
DELETE /api/pdf/1
```

**Rebuild Index:**
```bash
POST /api/reindex
```

### Search Response Format

```json
{
  "query": "Bangladesh",
  "search_type": "hybrid",
  "results": [
    {
      "filename": "annual_report.pdf",
      "pages": [
        {
          "page_number": 5,
          "snippet": "...the <mark>Bangladesh</mark> economy grew...",
          "relevance": 0.85
        }
      ]
    }
  ],
  "total_documents": 1
}
```

## Configuration

Edit `config.py` to customize:

```python
# Max upload size (500MB default)
MAX_CONTENT_LENGTH = 500 * 1024 * 1024

# Search settings
DEFAULT_SEARCH_TYPE = 'hybrid'  # keyword, semantic, hybrid
DEFAULT_RESULT_LIMIT = 20

# Text chunking for semantic search
CHUNK_SIZE = 500  # words per chunk
CHUNK_OVERLAP = 50  # overlap between chunks

# Embedding model
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
```

## Database Management

### Database Location
- SQLite: `database\pdf_index.db`
- ChromaDB: `database\chroma_db\`

### Inspect Database Directly
```bash
sqlite3 database\pdf_index.db

# View PDFs
sqlite> SELECT * FROM pdfs;

# View indexed content
sqlite> SELECT * FROM pdf_content;
```

### Rebuild ChromaDB Index
If semantic search isn''t working properly:
```bash
# Via API
POST /api/reindex
```

## Troubleshooting

### Common Issues

1. **No text extracted from PDF**
   - PDF may be scanned/image-based (OCR not supported)
   - PDF may be password protected
   - Check logs for extraction errors: `logs/error.log`

2. **Search returns no results**
   - Verify PDF was uploaded: GET /api/pdfs
   - Check if text extraction succeeded
   - Try simpler search terms

3. **Semantic search not working**
   - Rebuild index: POST /api/reindex
   - Check ChromaDB directory exists

4. **Port 5000 in use**
   - Find process: netstat -ano | findstr :5000
   - Kill it or change port in app.py

## Logging

The application uses Python's built-in `logging` module for structured logging.

### Log Files Location
```
logs/
├── app.log      # All INFO level and above
└── error.log    # ERROR level only (for troubleshooting)
```

### Log Format
```
2026-10-14 11:53:36 - __main__ - INFO - Search request: query='test', type=hybrid, limit=5
```

### Log Levels
- **INFO**: Normal operations (startup, searches, uploads, indexing)
- **ERROR**: Errors with full stack traces

### What's Logged
- Application startup/shutdown
- Search requests (query, type, number of results)
- File uploads and indexing progress
- PDF extraction errors
- ChromaDB operations

### Example Log Entries
```bash
# Application startup
2026-10-14 11:53:20 - __main__ - INFO - Application starting...

# Search request
2026-10-14 11:53:36 - __main__ - INFO - Search request: query='Bangladesh', type=hybrid, limit=20
2026-10-14 11:53:36 - __main__ - INFO - Search completed: hybrid found 2 documents for query 'Bangladesh'

# File upload
2026-10-14 11:54:01 - __main__ - INFO - Upload request: 1 file(s) received
2026-10-14 11:54:03 - __main__ - INFO - Successfully indexed report.pdf: 25 pages

# Error
2026-10-14 11:55:00 - services.keyword_search - ERROR - Keyword search error: ... (full traceback)
```

### Performance Tips

- PDF processing: ~1-2 seconds per page
- Search speed: < 1 second for 100+ PDFs
- Storage: Indexed text is ~10-20% of original PDF size

## Dependencies

```
Flask>=3.0.0
Werkzeug>=3.0.0
python-multipart>=0.0.6
pdfplumber>=0.10.3
sentence-transformers>=2.7.0
chromadb>=0.5.0
numpy>=1.24.0
torch>=2.0.0
torchvision>=0.15.0
```

## Note

This application runs locally without requiring any external paid APIs. All embeddings are computed locally using the sentence-transformers library.
