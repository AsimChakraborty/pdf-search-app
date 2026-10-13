# PDF Search Application
import os, sqlite3
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import pdfplumber

app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database', 'pdf_index.db')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(DATABASE), exist_ok=True)

# Init DB
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS pdfs (id INTEGER PRIMARY KEY, filename TEXT, filepath TEXT, upload_date TIMESTAMP)')
cursor.execute('CREATE VIRTUAL TABLE IF NOT EXISTS pdf_content USING fts5(pdf_id, filename, page_number, content, tokenize="porter unicode61")')
conn.commit()
conn.close()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in 'pdf'

def extract_text_from_pdf(pdf_path):
    pages_data = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text()
                if text and text.strip():
                    pages_data.append({'page_number': page_num, 'content': text})
    except Exception as e:
        print(f'Error: {e}')
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
    return len(pages_data)

def search_pdfs(query, limit=1000):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # Keep original query for highlighting and split into words
    original_query = query.strip()
    query_lower = original_query.lower()
    words = [w.strip() for w in query_lower.split() if w.strip()]
    
    if not words:
        return []
    
    try:
        # Build OR query for all words (finds pages with ANY word)
        like_patterns = [f'%{w}%' for w in words]
        
        # Simple query without complex CASE for snippet position
        if len(words) == 1:
            # Single word - simple LIKE
            where_clause = 'LOWER(content) LIKE ?'
            params = like_patterns + [limit]
            snippet_query = 'substr(pc.content, INSTR(LOWER(pc.content), ?), 250)'
            # snippet_params = like_patterns[0]
            snippet_params = words[0]
        else:
            # Multiple words - OR logic
            conditions = ['LOWER(content) LIKE ?' for _ in words]
            where_clause = ' OR '.join(conditions)
            # Use first word for snippet position
            snippet_query = 'substr(pc.content, INSTR(LOWER(pc.content), ?), 250)'
            snippet_params = words[0]
            params = like_patterns + [limit]
        
        # Search query
        search_sql = f'''SELECT p.filename, pc.page_number, pc.content,
            {snippet_query} as snippet
            FROM pdf_content pc
            JOIN pdfs p ON pc.pdf_id = p.id
            WHERE {where_clause}
            ORDER BY p.filename, pc.page_number
            LIMIT ?'''
        
        if len(words) == 1:
            cursor.execute(search_sql, like_patterns + params)
        else:
            cursor.execute(search_sql, [snippet_params] + params)
        
        results = cursor.fetchall()
        
        # Group by filename with unique pages
        grouped = {}
        for filename, page_number, content, snippet in results:
            if filename not in grouped:
                grouped[filename] = {'filename': filename, 'pages': []}
            existing_pages = [p['page_number'] for p in grouped[filename]['pages']]
            if page_number not in existing_pages:
                # Highlight each word in the snippet
                marked_snippet = snippet
                for word in words:
                    if word:
                        import re
                        pattern = re.compile(re.escape(word), re.IGNORECASE)
                        marked_snippet = pattern.sub(f'<mark>{word}</mark>', marked_snippet)
                grouped[filename]['pages'].append({'page_number': page_number, 'snippet': marked_snippet})
        
        return list(grouped.values())
    except Exception as e:
        print(f'Search error: {e}')
        import traceback
        traceback.print_exc()
        return []
    finally:
        conn.close()

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
    cursor.execute('SELECT filepath FROM pdfs WHERE id = ?', (pdf_id,))
    result = cursor.fetchone()
    if result:
        filepath = result[0]
        cursor.execute('DELETE FROM pdf_content WHERE pdf_id = ?', (pdf_id,))
        cursor.execute('DELETE FROM pdfs WHERE id = ?', (pdf_id,))
        conn.commit()
        conn.close()
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
        print(f'Upload error: {e}')
        return jsonify({'error': str(e), 'uploaded': [], 'errors': []}), 500

@app.route('/api/search', methods=['GET'])
def search():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'error': 'No search query provided', 'results': [], 'total_documents': 0}), 400
        results = search_pdfs(query)
        return jsonify({'query': query, 'results': results, 'total_documents': len(results)})
    except Exception as e:
        print(f'Search error: {e}')
        return jsonify({'error': str(e), 'results': [], 'total_documents': 0}), 500

@app.route('/api/pdfs', methods=['GET'])
def list_pdfs():
    try:
        pdfs = get_all_pdfs()
        return jsonify({'pdfs': pdfs, 'total': len(pdfs)})
    except Exception as e:
        print(f'List error: {e}')
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

@app.route('/static/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
