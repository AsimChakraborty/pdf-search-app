"""PDF Search Application
Supports keyword, semantic, and hybrid search"""
import os, sqlite3
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import pdfplumber

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'pdf_index.db')
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'chroma_db')

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)
os.makedirs(CHROMA_DB_PATH, exist_ok=True)

# Import services
from services.keyword_search import search_keyword
from services.semantic_search import search_semantic, index_pdf_to_chroma, delete_pdf_from_chroma, rebuild_chroma_index
from services.hybrid_search import search_hybrid, search_all_types
from services import improve_text_spacing

# Database initialization
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS pdfs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT NOT NULL,
    filepath TEXT NOT NULL,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS pdf_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pdf_id INTEGER NOT NULL,
    filename TEXT NOT NULL,
    page_number INTEGER NOT NULL,
    content TEXT)''')
conn.commit()
conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

def extract_text_from_pdf(pdf_path):
    pages_data = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text and text.strip():
                    text = improve_text_spacing(text)
                    pages_data.append({'page_number': page_num, 'content': text})
    except Exception as e:
        print(f'Error extracting PDF: {e}')
    return pages_data

def index_pdf(filepath, filename):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO pdfs (filename, filepath) VALUES (?, ?)', (filename, filepath))
    pdf_id = cursor.lastrowid
    pages_data = extract_text_from_pdf(filepath)
    for page in pages_data:
        cursor.execute('INSERT INTO pdf_content (pdf_id, filename, page_number, content) VALUES (?, ?, ?, ?)',
            (pdf_id, filename, page['page_number'], page['content']))
    conn.commit()
    conn.close()
    try:
        index_pdf_to_chroma(pdf_id, filename)
    except Exception as e:
        print(f'Error indexing to ChromaDB: {e}')
    return len(pages_data)

def get_all_pdfs():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, filename, filepath, upload_date FROM pdfs ORDER BY upload_date DESC')
    pdfs = cursor.fetchall()
    conn.close()
    return [{'id': p[0], 'filename': p[1], 'filepath': p[2], 'upload_date': p[3]} for p in pdfs]

def delete_pdf(pdf_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('SELECT filename, filepath FROM pdfs WHERE id = ?', (pdf_id,))
    result = cursor.fetchone()
    if result:
        filename, filepath = result
        cursor.execute('DELETE FROM pdf_content WHERE pdf_id = ?', (pdf_id,))
        cursor.execute('DELETE FROM pdfs WHERE id = ?', (pdf_id,))
        conn.commit()
        conn.close()
        try:
            delete_pdf_from_chroma(pdf_id)
        except:
            pass
        if os.path.exists(filepath):
            os.remove(filepath)
        return True
    conn.close()
    return False

@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def upload_files():
    try:
        if 'files[]' not in request.files:
            return jsonify({'error': 'No files provided', 'uploaded': [], 'errors': []}), 400
        files = request.files.getlist('files[]')
        if not files or files[0].filename == '':
            return jsonify({'error': 'No files selected', 'uploaded': [], 'errors': []}), 400
        results = {'uploaded': [], 'errors': []}
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                base_name, ext = os.path.splitext(filename)
                counter = 1
                while os.path.exists(filepath):
                    filename = f'{base_name}_{counter}{ext}'
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    counter += 1
                file.save(filepath)
                try:
                    pages_indexed = index_pdf(filepath, filename)
                    results['uploaded'].append({'filename': filename, 'pages': pages_indexed})
                except Exception as e:
                    print(f'Error indexing {filename}: {e}')
                    results['errors'].append({'filename': filename, 'error': str(e)})
                    if os.path.exists(filepath):
                        os.remove(filepath)
            else:
                results['errors'].append({'filename': file.filename if file else 'unknown', 'error': 'Invalid file type'})
        return jsonify(results)
    except Exception as e:
        return jsonify({'error': str(e), 'uploaded': [], 'errors': []}), 500

@app.route('/api/search', methods=['GET'])
def search():
    try:
        query = request.args.get('q', '').strip()
        search_type = request.args.get('type', 'hybrid').lower()
        limit = int(request.args.get('limit', 20))
        if not query:
            return jsonify({'error': 'No search query provided', 'results': [], 'total_documents': 0}), 400
        if search_type == 'keyword':
            results = search_keyword(query, limit)
        elif search_type == 'semantic':
            results = search_semantic(query, limit)
        elif search_type == 'hybrid':
            results = search_hybrid(query, limit)
        else:
            return jsonify({'error': 'Invalid search type. Use: keyword, semantic, or hybrid'}), 400
        return jsonify({'query': query, 'search_type': search_type, 'results': results, 'total_documents': len(results)})
    except Exception as e:
        print(f'Search error: {e}'); import traceback; traceback.print_exc()
        return jsonify({'error': str(e), 'results': [], 'total_documents': 0}), 500

@app.route('/api/search/all', methods=['GET'])
def search_all():
    try:
        query = request.args.get('q', '').strip()
        limit = int(request.args.get('limit', 20))
        if not query:
            return jsonify({'error': 'No search query provided'}), 400
        results = search_all_types(query, limit)
        return jsonify({'query': query, **results})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pdfs', methods=['GET'])
def list_pdfs():
    try:
        pdfs = get_all_pdfs()
        return jsonify({'pdfs': pdfs, 'total': len(pdfs)})
    except Exception as e:
        return jsonify({'error': str(e), 'pdfs': [], 'total': 0}), 500

@app.route('/api/pdf/<int:pdf_id>', methods=['DELETE'])
def delete_pdf_api(pdf_id):
    try:
        success = delete_pdf(pdf_id)
        if success:
            return jsonify({'message': 'PDF deleted successfully'})
        else:
            return jsonify({'error': 'PDF not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/reindex', methods=['POST'])
def reindex_all():
    try:
        count = rebuild_chroma_index()
        return jsonify({'message': f'Reindexed {count} pages', 'pages': count})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/static/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
