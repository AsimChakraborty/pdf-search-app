"""
PDF API Routes
Handles PDF upload, delete, list, and view operations
"""
import os
from flask import Blueprint, request, jsonify, send_from_directory

# Models
from models import insert_pdf, get_all_pdfs, get_pdf_by_id
from models import delete_pdf as delete_pdf_db, insert_pdf_content

# Services
from services import extract_text_from_pdf
from services.semantic_search import index_pdf_to_chroma, delete_pdf_from_chroma

# Utils
from utils import allowed_file, get_upload_folder, get_unique_filename
from utils import get_file_path, delete_file

# Setup logging
from services.log_config import get_logger
logger = get_logger(__name__)

# Create blueprint
pdf_bp = Blueprint('pdf', __name__, url_prefix='/api')


@pdf_bp.route('/', methods=['GET'])
def list_pdfs():
    """List all uploaded PDFs"""
    try:
        pdfs = get_all_pdfs()
        return jsonify({'pdfs': pdfs, 'total': len(pdfs)})
    except Exception as e:
        logger.error(f"Error listing PDFs: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@pdf_bp.route('/<int:pdf_id>', methods=['GET'])
def view_pdf(pdf_id):
    """View a specific PDF"""
    try:
        pdf = get_pdf_by_id(pdf_id)
        if not pdf:
            return jsonify({'error': 'PDF not found'}), 404
        return jsonify(pdf)
    except Exception as e:
        logger.error(f"Error viewing PDF: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@pdf_bp.route('/<int:pdf_id>', methods=['DELETE'])
def delete_pdf(pdf_id):
    """Delete a PDF"""
    try:
        filepath = delete_pdf_db(pdf_id)
        if not filepath:
            return jsonify({'error': 'PDF not found'}), 404
        
        try:
            delete_pdf_from_chroma(pdf_id)
        except Exception as e:
            logger.warning(f"ChromaDB delete failed: {e}")
        
        delete_file(filepath)
        logger.info(f"Deleted PDF ID: {pdf_id}")
        return jsonify({'message': 'PDF deleted successfully'})
    except Exception as e:
        logger.error(f"Error deleting PDF: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@pdf_bp.route('/upload', methods=['POST'])
def upload_files():
    """Upload PDF files"""
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files provided', 'uploaded': [], 'errors': []}), 400
        
        files = request.files.getlist('files[]')
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected', 'uploaded': [], 'errors': []}), 400
        
        logger.info(f"Upload request: {len(files)} file(s) received")
        
        upload_folder = get_upload_folder()
        results = {'uploaded': [], 'errors': []}
        
        for file in files:
            if file and allowed_file(file.filename):
                filename = get_unique_filename(file.filename, upload_folder)
                filepath = get_file_path(filename, upload_folder)
                file.save(str(filepath))
                logger.info(f"Saved file: {filename}")
                
                try:
                    pdf_id = insert_pdf(filename, str(filepath))
                    pages_data = extract_text_from_pdf(str(filepath))
                    
                    for page in pages_data:
                        insert_pdf_content(pdf_id, filename, page['page_number'], page['content'])
                    
                    try:
                        index_pdf_to_chroma(pdf_id, filename)
                    except Exception as e:
                        logger.warning(f"ChromaDB indexing failed: {e}")
                    
                    results['uploaded'].append({'filename': filename, 'pages': len(pages_data), 'id': pdf_id})
                    logger.info(f"Indexed {filename}: {len(pages_data)} pages")
                except Exception as e:
                    logger.error(f"Error indexing {filename}: {e}", exc_info=True)
                    results['errors'].append({'filename': filename, 'error': str(e)})
                    delete_file(str(filepath))
            else:
                results['errors'].append({'filename': file.filename if file else 'unknown', 'error': 'Invalid file type'})
        
        return jsonify(results)
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        return jsonify({'error': str(e), 'uploaded': [], 'errors': []}), 500


@pdf_bp.route('/rebuild', methods=['POST'])
def rebuild_index():
    """Rebuild the search index"""
    try:
        from services.semantic_search import rebuild_chroma_index
        rebuild_chroma_index()
        return jsonify({'message': 'Index rebuilt successfully'})
    except Exception as e:
        logger.error(f"Rebuild error: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500