"""
Invitation Automation System - Main Application
A Flask web application for creating personalized PDF invitations and sending via WhatsApp
"""
from flask import Flask, render_template, request, jsonify, send_file, session
import os
import uuid
from werkzeug.utils import secure_filename
import base64

from pdf_handler import add_name_to_pdf, get_pdf_preview, get_pdf_dimensions, get_pdf_page_count
from excel_handler import read_contacts, validate_excel_file

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
FONT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'fonts', 'NotoSansGujarati-Regular.ttf')

ALLOWED_PDF = {'pdf'}
ALLOWED_EXCEL = {'xlsx'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


@app.route('/')
def index():
    """Main page with upload form and preview"""
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle PDF and Excel file uploads"""
    try:
        # Check if files are present
        if 'pdf_file' not in request.files:
            return jsonify({'success': False, 'message': 'No PDF file uploaded'})
        
        if 'excel_file' not in request.files:
            return jsonify({'success': False, 'message': 'No Excel file uploaded'})
        
        pdf_file = request.files['pdf_file']
        excel_file = request.files['excel_file']
        
        if pdf_file.filename == '' or excel_file.filename == '':
            return jsonify({'success': False, 'message': 'No files selected'})
        
        # Validate file types
        if not allowed_file(pdf_file.filename, ALLOWED_PDF):
            return jsonify({'success': False, 'message': 'Invalid PDF file. Must be a .pdf file'})
        
        if not allowed_file(excel_file.filename, ALLOWED_EXCEL):
            return jsonify({'success': False, 'message': 'Invalid Excel file. Must be a .xlsx file'})
        
        # Generate unique session ID for this upload
        session_id = str(uuid.uuid4())
        session['session_id'] = session_id
        
        # Create session folder
        session_folder = os.path.join(UPLOAD_FOLDER, session_id)
        os.makedirs(session_folder, exist_ok=True)
        
        # Save files
        pdf_filename = secure_filename(pdf_file.filename)
        excel_filename = secure_filename(excel_file.filename)
        
        pdf_path = os.path.join(session_folder, pdf_filename)
        excel_path = os.path.join(session_folder, excel_filename)
        
        pdf_file.save(pdf_path)
        excel_file.save(excel_path)
        
        # Validate Excel file
        validation = validate_excel_file(excel_path)
        if not validation['valid']:
            return jsonify({'success': False, 'message': validation['message']})
        
        # Get PDF info
        page_count = get_pdf_page_count(pdf_path)
        dimensions = get_pdf_dimensions(pdf_path)
        
        # Store paths in session
        session['pdf_path'] = pdf_path
        session['excel_path'] = excel_path
        
        return jsonify({
            'success': True,
            'message': f'Files uploaded successfully. Found {validation["count"]} contacts.',
            'session_id': session_id,
            'contact_count': validation['count'],
            'page_count': page_count,
            'pdf_width': dimensions[0],
            'pdf_height': dimensions[1]
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error uploading files: {str(e)}'})


@app.route('/preview/<session_id>')
def get_preview(session_id):
    """Get PDF preview as PNG image"""
    try:
        page_num = request.args.get('page', 0, type=int)
        zoom = request.args.get('zoom', 1.5, type=float)
        
        # Find PDF in session folder
        session_folder = os.path.join(UPLOAD_FOLDER, session_id)
        pdf_files = [f for f in os.listdir(session_folder) if f.endswith('.pdf')]
        
        if not pdf_files:
            return jsonify({'error': 'No PDF found'}), 404
        
        pdf_path = os.path.join(session_folder, pdf_files[0])
        
        # Generate preview
        png_bytes = get_pdf_preview(pdf_path, page_num, zoom)
        
        # Return as base64 for embedding in HTML
        return send_file(
            __import__('io').BytesIO(png_bytes),
            mimetype='image/png'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/preview-with-name/<session_id>')
def preview_with_name(session_id):
    """Generate a preview with a sample name placed"""
    try:
        x = request.args.get('x', 100, type=float)
        y = request.args.get('y', 100, type=float)
        font_size = request.args.get('fontSize', 24, type=int)
        font_color = request.args.get('fontColor', '#000000')
        font_family = request.args.get('fontFamily', 'helv')
        sample_name = request.args.get('name', 'John Doe')
        page_num = request.args.get('page', 0, type=int)
        zoom = request.args.get('zoom', 1.5, type=float)
        
        # Convert hex color to RGB tuple (0-1 range)
        hex_color = font_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        
        # Find PDF
        session_folder = os.path.join(UPLOAD_FOLDER, session_id)
        pdf_files = [f for f in os.listdir(session_folder) if f.endswith('.pdf')]
        
        if not pdf_files:
            return jsonify({'error': 'No PDF found'}), 404
        
        pdf_path = os.path.join(session_folder, pdf_files[0])
        
        # Create temp PDF with name
        import tempfile
        temp_pdf = tempfile.NamedTemporaryFile(suffix='.pdf', delete=False)
        temp_pdf.close()
        
        # Determine font settings
        font_path = None
        font_name = font_family
        
        if font_family == 'gujarati':
            font_path = FONT_PATH
            font_name = 'custom_font'
            
        add_name_to_pdf(
            pdf_path=pdf_path,
            name=sample_name,
            x=x / zoom,  # Convert from zoomed coordinates
            y=y / zoom,
            page_num=page_num,
            font_size=font_size,
            font_color=(r, g, b),
            font_name=font_name,
            font_path=font_path,
            output_path=temp_pdf.name
        )
        
        # Get preview of the temp PDF
        png_bytes = get_pdf_preview(temp_pdf.name, page_num, zoom)
        
        # Clean up temp file
        os.unlink(temp_pdf.name)
        
        return send_file(
            __import__('io').BytesIO(png_bytes),
            mimetype='image/png'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/contacts/<session_id>')
def get_contacts(session_id):
    """Get list of contacts from uploaded Excel"""
    try:
        session_folder = os.path.join(UPLOAD_FOLDER, session_id)
        excel_files = [f for f in os.listdir(session_folder) if f.endswith('.xlsx')]
        
        if not excel_files:
            return jsonify({'error': 'No Excel file found'}), 404
        
        excel_path = os.path.join(session_folder, excel_files[0])
        contacts = read_contacts(excel_path)
        
        return jsonify({
            'success': True,
            'contacts': contacts
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/generate-only', methods=['POST'])
def generate_only():
    """Generate personalized PDFs"""
    try:
        data = request.json
        session_id = data.get('session_id')
        x = data.get('x', 100)
        y = data.get('y', 100)
        font_size = data.get('fontSize', 24)
        font_color = data.get('fontColor', '#000000')
        font_family = data.get('fontFamily', 'helv')
        page_num = data.get('pageNum', 0)
        zoom = data.get('zoom', 1.5)
        
        # Convert hex color to RGB
        hex_color = font_color.lstrip('#')
        r = int(hex_color[0:2], 16) / 255
        g = int(hex_color[2:4], 16) / 255
        b = int(hex_color[4:6], 16) / 255
        
        # Get files
        session_folder = os.path.join(UPLOAD_FOLDER, session_id)
        pdf_files = [f for f in os.listdir(session_folder) if f.endswith('.pdf')]
        excel_files = [f for f in os.listdir(session_folder) if f.endswith('.xlsx')]
        
        if not pdf_files or not excel_files:
            return jsonify({'success': False, 'message': 'Files not found'})
        
        pdf_path = os.path.join(session_folder, pdf_files[0])
        excel_path = os.path.join(session_folder, excel_files[0])
        
        # Read contacts
        contacts = read_contacts(excel_path)
        
        # Create output folder for this session
        output_session_folder = os.path.join(OUTPUT_FOLDER, session_id)
        os.makedirs(output_session_folder, exist_ok=True)
        
        generated_files = []
        
        for contact in contacts:
            name = contact['name']
            
            # Filename logic: Truncate name to 15 chars (unicode aware slice), 
            # then make safe for filesystem. 
            # Note: The pdf_handler also applies some safety logic, but we can override path here.
            # Let's trust pdf_handler's safety logic if we just pass name, 
            # BUT the requirements said "make name of the pdf like first 15 charector of name, Which can be any gujrati of english"
            # So I should handle that explicitly here or in pdf_handler. I added it to pdf_handler.
            # Wait, I added it to pdf_handler but I should pass output_path explicit to be sure? 
            # Actually pdf_handler has the safe logic now. Let's rely on pdf_handler to do it 
            # OR better, generate the path here and pass it to be 100% sure.
            
            # Python slice is unicode aware.
            short_name = name[:15]
            safe_name = "".join(c for c in short_name if c.isalnum() or c in (' ', '-', '_', '.')).strip()
            safe_name = safe_name.replace(' ', '_')
            output_pdf_path = os.path.join(output_session_folder, f"invitation_{safe_name}.pdf")
            
            # Determine font settings
            font_path = None
            font_name = font_family
            
            if font_family == 'gujarati':
                font_path = FONT_PATH
                font_name = 'custom_font'
                
            add_name_to_pdf(
                pdf_path=pdf_path,
                name=name,
                x=x / zoom,
                y=y / zoom,
                page_num=page_num,
                font_size=font_size,
                font_color=(r, g, b),
                font_name=font_name,
                font_path=font_path,
                output_path=output_pdf_path
            )
            
            generated_files.append({
                'name': name,
                'path': output_pdf_path
            })
        
        return jsonify({
            'success': True,
            'message': f'Generated {len(generated_files)} personalized invitations.',
            'files': generated_files,
            'output_folder': output_session_folder
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': f'Error: {str(e)}'})


if __name__ == '__main__':
    print("=" * 60)
    print("🎉 Invitation Automation System")
    print("=" * 60)
    print("Open http://localhost:5000 in your browser")
    print("-" * 60)
    print("Instructions:")
    print("1. Upload your PDF invitation template")
    print("2. Upload your Excel file with Name and Mobile columns")
    print("3. Click on the PDF preview to set where names appear")
    print("4. Adjust font size and color")
    print("5. Click 'Generate PDFs' to create invitations")
    print("=" * 60)
    # app.run(debug=True, port=5000)
