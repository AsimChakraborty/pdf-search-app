
from flask import Flask, render_template, send_from_directory

# Setup logging (must be first)
from services.log_config import get_logger
logger = get_logger(__name__)

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB

# Ensure directories exist
from utils import get_upload_folder
get_upload_folder()  # Creates static/uploads if not exists

# Initialize database
from models import init_database
logger.info("Application starting...")

# Register blueprints
from api import pdf_bp, search_bp

app.register_blueprint(pdf_bp, url_prefix='/api')
app.register_blueprint(search_bp, url_prefix='/api')

# Serve uploaded files
from utils import get_upload_folder

@app.route('/static/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(get_upload_folder(), filename)

# Home page
@app.route('/')
def index_page():
    return render_template('index.html')


if __name__ == '__main__':
    logger.info("Starting PDF Search Engine...")
    app.run(debug=True, host='0.0.0.0', port=5000)