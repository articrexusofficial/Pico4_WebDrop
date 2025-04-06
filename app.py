import os
import sqlite3
import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, send_from_directory
from werkzeug.utils import secure_filename
import uuid # For generating unique parts
from datetime import datetime  # Add this import

UPLOAD_FOLDER = 'output'
DATABASE = 'gallery.db'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'super secret key' # Change this in a real application

# --- Database Setup ---

def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS images (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_filename TEXT NOT NULL,
            stored_filename TEXT NOT NULL UNIQUE,
            upload_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row # Return rows as dictionary-like objects
    return conn

# --- Helper Functions ---

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_unique_filename(filename):
    """Generates a unique filename if the original already exists."""
    name, ext = os.path.splitext(filename)
    unique_filename = filename
    counter = 1
    # Check against the filesystem AND the database for robustness
    conn = get_db()
    cursor = conn.cursor()
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)) or \
          cursor.execute("SELECT 1 FROM images WHERE stored_filename = ?", (unique_filename,)).fetchone():
        unique_filename = f"{name}_{uuid.uuid4().hex[:6]}{ext}" # Add short UUID part
        # Fallback if somehow UUID still collides (highly unlikely)
        # unique_filename = f"{name}_{counter}{ext}"
        # counter += 1
    conn.close()
    return unique_filename

# --- Routes ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part')
        return redirect(url_for('index')) # Redirect to index
    file = request.files['file']

    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('index')) # Redirect to index

    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        stored_filename = generate_unique_filename(original_filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], stored_filename)

        try:
            # Ensure the upload folder exists (might be redundant but safe)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            file.save(file_path)

            # Add to database
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO images (original_filename, stored_filename) VALUES (?, ?)",
                (original_filename, stored_filename)
            )
            conn.commit()
            conn.close()

            flash(f'File "{original_filename}" uploaded successfully as "{stored_filename}"!')
            return redirect(url_for('index')) # Redirect back to index

        except sqlite3.Error as e:
             flash(f'Database error: {e}')
             # Clean up saved file if DB insert fails? Optional.
             if os.path.exists(file_path):
                 os.remove(file_path)
             return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error saving file: {e}')
            return redirect(url_for('index'))
    else:
        flash('File type not allowed')
        return redirect(url_for('index')) # Redirect to index

@app.route('/delete/<int:file_id>', methods=['POST'])
def delete_file(file_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT stored_filename FROM images WHERE id = ?", (file_id,))
    file = cursor.fetchone()
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file["stored_filename"])
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            cursor.execute("DELETE FROM images WHERE id = ?", (file_id,))
            conn.commit()
            flash("File deleted successfully.")
        except Exception as e:
            flash(f"Error deleting file: {e}")
    else:
        flash("File not found.")
    conn.close()
    return redirect(url_for('gallery'))

@app.route('/gallery')
def gallery():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, stored_filename, original_filename, upload_timestamp FROM images ORDER BY upload_timestamp DESC")
    images = cursor.fetchall()
    conn.close()

    # Convert upload_timestamp to date object
    images = [
        {
            **dict(image),
            "upload_timestamp": datetime.strptime(image["upload_timestamp"], "%Y-%m-%d %H:%M:%S").date()
            if image["upload_timestamp"] else None
        }
        for image in images
    ]

    return render_template('gallery.html', images=images)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    # Security: Ensure filename is safe before sending
    safe_filename = secure_filename(filename)
    if safe_filename != filename:
        # Abort if filename seems manipulated
        from flask import abort
        abort(404)
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], safe_filename)
    except FileNotFoundError:
        from flask import abort
        abort(404)


if __name__ == '__main__':
    # Ensure the upload folder exists at startup
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # Run on 0.0.0.0 to be accessible on the local network
    app.run(host='0.0.0.0', port=5000, debug=True)
