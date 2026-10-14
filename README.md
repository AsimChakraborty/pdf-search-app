# PDF Search Engine - AI Powered

A powerful web-based application for searching across multiple PDF documents using keyword, semantic (AI-powered), and hybrid search methods.

## Features

- Multiple PDF Upload: Upload 40+ PDFs simultaneously via drag-and-drop
- Keyword Search: Traditional full-text search using SQLite LIKE
- Semantic Search: AI-powered search using sentence embeddings
- Hybrid Search: Returns keyword-matched results with highlighting
- Fast Performance: Pre-indexed text enables sub-second search queries
- Persistent Storage: Data survives application restarts
- Modular Design: Clean separation of concerns for maintainability

## Architecture

```
Flask App (app.py)          <- Route registration only (~30 lines)
        |
    +---+---+---+
    |   |   |   |
   API Models Services Utils
```

## Project Structure

```
scan_test/
├── app.py                  # Flask app entry point
├── config.py               # Configuration
├── requirements.txt        # Python dependencies
│
├── api/                    # REST API routes
│   ├── pdf_routes.py       # Upload, delete, list
│   └── search_routes.py    # Search endpoints
│
├── models/                 # Database layer
│   ├── db.py               # Connection & init
│   └── pdf_repo.py         # PDF CRUD operations
│
├── services/               # Business logic
│   ├── __init__.py         # PDF extraction
│   ├── keyword_search.py   # Keyword search
│   ├── semantic_search.py  # Semantic search
│   ├── hybrid_search.py    # Hybrid search
│   └── embedding_service.py# Sentence embeddings
│
├── utils/                  # Helper functions
│   └── file_utils.py       # File operations
│
├── database/               # Data storage
├── static/uploads/         # Uploaded PDFs
├── templates/              # HTML templates
└── logs/                   # Application logs
```

## Why Modular Design?

| Layer | Responsibility | Benefits |
|-------|----------------|----------|
| api/ | HTTP routes | Easy to test |
| models/ | Database ops | Single source |
| services/ | Business logic | Reusable |
| utils/ | Helpers | DRY principle |

## Quick Start

### Prerequisites
- Python 3.12 or higher

### Installation
```bash
uv venv --python 3.12
uv pip install flask pdfplumber werkzeug sentence-transformers chromadb numpy torch torchvision
```

### Running
```bash
.venv\Scripts\python.exe app.py
```
Open: http://127.0.0.1:5000

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | Home page |
| GET | /api/ | List all PDFs |
| POST | /api/upload | Upload PDFs |
| DELETE | /api/<id> | Delete PDF |
| GET | /api/search | Search PDFs |
| POST | /api/rebuild | Rebuild index |

## Search Parameters
- q: Search query (required)
- type: keyword, semantic, or hybrid (default: hybrid)
- limit: Max results (default: 20)

## Search Types

### Keyword Search
- Uses SQLite LIKE queries
- Exact word/phrase matches with <mark> highlighting
- Best for: Exact matches

### Semantic Search
- Uses AI embeddings (all-MiniLM-L6-v2)
- Finds conceptually similar content
- Best for: Conceptual search, synonyms

### Hybrid Search
- Returns keyword-matched results only
- Includes highlighting
- Best for: Accuracy with context

## Configuration

Edit config.py:
```python
DEFAULT_SEARCH_TYPE = 'hybrid'
DEFAULT_RESULT_LIMIT = 20
CHUNK_SIZE = 500
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'
```

## Troubleshooting

1. No text extracted - PDF may be scanned/image-based
2. Search returns no results - verify PDF uploaded via GET /api/
3. Semantic search not working - rebuild: POST /api/rebuild
4. Port 5000 in use - netstat -ano | findstr :5000

## Logging
- logs/app.log - All INFO level and above
- logs/error.log - ERROR level only

## Dependencies
Flask>=3.0.0, Werkzeug>=3.0.0, pdfplumber>=0.10.3, sentence-transformers>=2.7.0, chromadb>=0.5.0, numpy>=1.24.0, torch>=2.0.0

This application runs locally without external paid APIs.