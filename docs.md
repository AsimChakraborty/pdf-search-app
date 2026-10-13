# Project Prompt: AI-Powered PDF Search Application Using Semantic and Hybrid Search

## Project Overview

I want to develop an AI-powered PDF Search Application using Python, Flask, SQLite, ChromaDB, and text embeddings.

The application should allow users to upload multiple PDF files, including 40 or more PDFs, and search across all uploaded documents to identify which PDFs and pages contain relevant information.

For example, a user uploads 40 PDF files and searches for **"business opportunity in Bangladesh."** The application should identify the relevant documents and pages, even when the exact search phrase does not appear in the PDF.

The application must support both traditional keyword search and AI-powered semantic search.

## 1. Existing Project

I already have a Flask application with the following features:

- Multiple PDF uploads.
- PDF text extraction using `pdfplumber`.
- SQLite database for PDF metadata and extracted text.
- SQLite FTS5 and `LIKE`-based keyword searching.
- API endpoints for uploading, searching, listing, and deleting PDFs.
- HTML-based frontend.

The current application can identify matching pages using keywords, but the extracted text is sometimes displayed without proper spacing, and the search results do not always capture relevant content.

Improve the existing project instead of rebuilding it unnecessarily. Preserve useful existing functionality and maintain compatibility with the current database wherever practical.

## 2. Required Technologies

Use the following technologies:

- **Python:** Main programming language.
- **Flask:** Backend API and web application.
- **pdfplumber:** PDF text extraction.
- **SQLite:** Store PDF metadata, page content, upload dates, and document records.
- **SQLite FTS5:** Traditional full-text keyword search.
- **Sentence Transformers:** Generate text embeddings using `all-MiniLM-L6-v2`.
- **ChromaDB:** Store embeddings and retrieve semantically similar text.
- **HTML, CSS, JavaScript, and Bootstrap:** Frontend interface.

The embedding model and vector database should run locally without requiring a paid external API.

## 3. Multiple PDF Upload

Users should be able to upload multiple PDF files in one operation.

Requirements:

- Support 40 or more PDFs, subject to available system resources.
- Validate file extensions and handle invalid files.
- Prevent filename collisions.
- Extract text page by page.
- Store each PDF's metadata and extracted text in SQLite.
- Generate embeddings for extracted text and store them in ChromaDB.
- Show upload progress and success or failure messages.
- Handle empty, corrupted, encrypted, and image-only PDFs gracefully.
- Avoid indexing the same PDF multiple times accidentally.

For large uploads, use a reliable processing workflow that does not require every PDF to finish processing before the upload interface can respond.

## 4. PDF Text Extraction and Chunking

Extract text from each PDF while preserving page numbers and as much of the original reading order as possible.

Requirements:

- Improve whitespace and word-spacing handling.
- Preserve meaningful paragraph breaks.
- Handle multi-column layouts and tables as well as reasonably possible.
- Split long page content into smaller, overlapping text chunks for embedding.
- Use approximately 300–500 words per chunk as a starting point, with configurable overlap.
- Store the source PDF ID, filename, page number, and chunk ID as metadata.
- Ensure every search result can be traced back to its original PDF and page.
- Detect pages with little or no extractable text and optionally process scanned PDFs using OCR, such as Tesseract.

Do not assume that normalizing whitespace will fix every PDF layout problem.

## 5. Semantic Search Using Text Embeddings

Implement semantic search using Sentence Transformers and ChromaDB.

The workflow should be:

1. Extract text from uploaded PDFs.
2. Split the text into chunks while preserving source page information.
3. Generate embeddings for each chunk using `all-MiniLM-L6-v2`.
4. Store the embeddings and metadata in ChromaDB.
5. Convert each user query into an embedding.
6. Retrieve the most semantically similar chunks.
7. Group matching chunks by PDF and page number.
8. Return readable text previews and relevant metadata.

Example:

PDF content:

"The proposed service creates recurring revenue opportunities by serving families who need reliable personal care assistance."

User query:

"Business opportunities in Bangladesh"

The system should be able to retrieve this content when it is sufficiently relevant, even if the exact phrase does not appear.

Use cosine similarity or another appropriate distance metric. Explain the meaning of the distance scores and do not present them as calibrated confidence percentages.

## 6. Hybrid Search

Implement hybrid search by combining:

- SQLite FTS5 keyword search.
- ChromaDB semantic search.

Keyword search should help find exact words, names, numbers, and specific phrases. Semantic search should help identify conceptually related information and paraphrases.

Combine the results using an appropriate ranking strategy, such as Reciprocal Rank Fusion (RRF), or another justified approach.

Requirements:

- Avoid duplicate results.
- Rank the most relevant results first.
- Support multiple search terms.
- Provide an option to use keyword-only, semantic-only, or hybrid search.
- Make the search method configurable.
- Do not use simple OR-based keyword matching as the only relevance-ranking strategy.
- Ensure that the result limit does not prevent relevant pages from being retrieved unnecessarily.

## 7. Search Results Interface

Build a clean, responsive interface with:

- A search input field.
- A search button.
- A search mode selector: Keyword, Semantic, and Hybrid.
- A list of matching PDF documents.
- The filename of each matching PDF.
- Matching page numbers.
- Relevant text previews with highlighted keyword matches where applicable.
- A link or button to open the original PDF at the relevant page when supported.
- A count of matching documents and pages.
- Loading indicators, empty states, and error messages.
- Pagination or a load-more mechanism for large result sets.

Group results by PDF while retaining the individual matching pages and relevant snippets.

For semantic results, use the original extracted text as the preview and show a similarity or ranking indicator only when its meaning is clearly explained.

## 8. API Endpoints

Maintain and improve the existing Flask API.

### POST `/api/upload`

Upload multiple PDFs and initiate extraction and indexing.

### GET `/api/search?q=business%20opportunity&mode=hybrid`

Search the indexed PDFs using the selected search method.

Supported modes:

- `keyword`
- `semantic`
- `hybrid`

### GET `/api/pdfs`

Return the list of uploaded PDFs and their processing status.

### DELETE `/api/pdf/<pdf_id>`

Delete the selected PDF and its associated records, extracted text, and vectors.

### GET `/api/pdf/<pdf_id>`

Return metadata for an individual PDF.

Use appropriate HTTP status codes, parameter validation, error handling, and consistent JSON response structures.

If background processing is implemented, expose processing status so the frontend can distinguish between uploaded, processing, indexed, and failed documents.

## 9. Database and Index Synchronization

Keep SQLite and ChromaDB synchronized.

Requirements:

- Maintain a stable PDF ID and unique chunk IDs.
- Prevent duplicate vector records.
- Ensure deletion removes associated vectors.
- Support safe re-indexing when extraction logic or embedding models change.
- Provide a migration utility to index PDFs already stored in the existing SQLite database.
- Handle partial failures so that a PDF is not incorrectly reported as successfully indexed.
- Record the embedding model and indexing version where appropriate.
- Explain how to rebuild the vector index without losing the original uploaded PDFs.

Do not assume existing SQLite records are automatically available in ChromaDB.

## 10. Suggested Project Structure

Organize the project into maintainable modules.

scan-test/
- app.py
- config.py
- requirements.txt
- README.md
- database/
- static/
  - css/
  - js/
  - uploads/
- templates/
  - index.html
- services/
  - pdf_extractor.py
  - keyword_search.py
  - embedding_service.py
  - semantic_search.py
  - hybrid_search.py
  - indexing_service.py
- routes/
  - upload_routes.py
  - search_routes.py
  - pdf_routes.py
- scripts/
  - migrate_existing_pdfs.py
  - rebuild_vector_index.py
- tests/

You may adjust the structure if necessary, but keep responsibilities clearly separated.

## 11. Performance and Reliability

- Reuse the embedding model rather than loading it for every search request.
- Reuse database and vector-store configurations appropriately.
- Avoid regenerating embeddings for unchanged documents.
- Support configurable result limits.
- Add logging instead of relying exclusively on `print()`.
- Validate uploaded file types and handle large files safely.
- Use background jobs if PDF extraction and embedding generation take too long for synchronous requests.
- Keep the application usable on a typical development computer without a dedicated GPU.
- Document the disk-space, RAM, and CPU considerations.

## 12. Testing and Validation

Provide tests for:

- Uploading multiple PDFs.
- Extracting text and preserving page numbers.
- Searching for exact keywords.
- Searching for related concepts using semantic search.
- Comparing keyword, semantic, and hybrid results.
- Deleting PDFs and their vectors.
- Re-indexing existing PDFs.
- Handling duplicate uploads and failed indexing.
- Searching when no documents exist.
- Searching scanned PDFs that require OCR.

Create a small test dataset with known expected search results. Evaluate retrieval quality using measures such as Precision@K, Recall@K, or Mean Reciprocal Rank where appropriate.

Do not claim that semantic search will always identify every relevant page. Validate retrieval quality with actual test queries.

## 13. Deliverables

Provide:

1. The complete working project code.
2. The full folder structure.
3. A `requirements.txt` file.
4. Instructions for creating a virtual environment and installing dependencies.
5. Instructions for running the application on Windows.
6. Instructions for testing the APIs.
7. A migration script for existing PDF records.
8. A script for rebuilding the ChromaDB index.
9. A clear explanation of how keyword search, semantic search, and hybrid ranking work.
10. A professional README with setup, configuration, API documentation, troubleshooting, and limitations.

Write complete, consistent, copy-paste-ready code rather than isolated snippets. Ensure that all imports, routes, database operations, frontend requests, and indexing workflows work together.

Start by reviewing my existing Flask application and identifying its current problems. Then provide an implementation plan and build the improved application step by step, preserving existing functionality wherever practical.