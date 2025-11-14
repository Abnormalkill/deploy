# app.py
import os
import datetime
import sys
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_pymongo import PyMongo 
from flask_bcrypt import Bcrypt
from flask_socketio import SocketIO, emit, join_room
from werkzeug.utils import secure_filename
from models import User, Message, Material
from bson.objectid import ObjectId

# --- Initialization & Configuration ---
load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.secret_key = os.getenv("SECRET_KEY")

# File Upload Configuration
UPLOAD_FOLDER = 'static/study_materials'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'pptx'}

# Initialize extensions
mongo = PyMongo(app) 
bcrypt = Bcrypt(app) 
socketio = SocketIO(app)

# --- CRITICAL DATABASE CONNECTION CHECK ---
with app.app_context():
    try:
        mongo.db.client.list_database_names()
        print("--- MongoDB connection SUCCESSFUL. ---")
    except Exception as e:
        print("!!! FATAL ERROR: MongoDB connection FAILED. !!!")
        print(f"Error details: {e}")
        sys.exit(1)


# --- Helper Functions ---

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.find_by_id(mongo, user_id)
    return None

def allowed_file(filename):
    """Checks if a file's extension is in the allowed set."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Routes ---

@app.route('/')
def index():
    current_user = get_current_user()
    return render_template('index.html', user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name') 

        if User.find_by_email(mongo, email):
            flash("Email already registered.", 'error')
            return redirect(url_for('register'))

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email, hashed_password, name)
        new_user.save_to_db(mongo)

        flash(f"Welcome, {name}! Account created successfully. Please log in.", 'success')
        return redirect(url_for('login'))
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user_data = User.find_by_email(mongo, email)
        
        if user_data and bcrypt.check_password_hash(user_data['password'], password):
            session['user_id'] = str(user_data['_id'])
            flash("Login successful! Welcome.", 'success')
            return redirect(url_for('study_hub'))
        else:
            flash("Invalid email or password.", 'error')
            return redirect(url_for('login'))
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("You have been logged out.", 'info')
    return redirect(url_for('index'))

@app.route('/study-hub', methods=['GET', 'POST'])
def study_hub():
    current_user = get_current_user()
    if not current_user:
        flash("You must be logged in to view the Study Hub.", 'error')
        return redirect(url_for('login'))
    
    # --- File Upload Logic ---
    if request.method == 'POST':
        if 'study_file' not in request.files:
            flash("No file part in the request.", 'error')
            return redirect(url_for('study_hub'))
        
        file = request.files['study_file']
        
        if file.filename == '':
            flash("No file selected for uploading.", 'error')
            return redirect(url_for('study_hub'))

        if file and allowed_file(file.filename):
            original_filename = file.filename
            secure_name = secure_filename(original_filename)
            
            if not os.path.exists(app.config['UPLOAD_FOLDER']):
                os.makedirs(app.config['UPLOAD_FOLDER'])
                
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_name)
            file.save(save_path)
            
            file_url = url_for('uploaded_file', filename=secure_name)

            # Get name from current user for display
            uploader_name = current_user.get('name', current_user['email']) 
            
            Material.save_material(
                mongo, 
                session['user_id'], 
                uploader_name,
                original_filename,
                file_url
            )
            flash(f"File '{original_filename}' uploaded successfully!", 'success')
            return redirect(url_for('study_hub'))
        else:
            flash("File upload failed. File type not allowed.", 'error')
            return redirect(url_for('study_hub'))

    # Load data for rendering
    messages = Message.get_recent_messages(mongo)
    materials = Material.get_all_materials(mongo)
    
    return render_template('hub.html', user=current_user, messages=messages, materials=materials)

# File Download Route: FORCES DOWNLOAD using as_attachment=True
@app.route('/static/study_materials/<filename>')
def uploaded_file(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'], 
        filename, 
        as_attachment=True
    )

# --- SocketIO (Chat) Events ---

@socketio.on('connect')
def handle_connect():
    if session.get('user_id'):
        join_room('global_chat')

@socketio.on('send_message')
def handle_send_message(data):
    user = get_current_user()
    if user:
        content = data['message']
        
        # Use user's Name for display, fallback to email
        sender_name = user.get('name', user.get('email', 'Unknown User')) 
        
        # 1. Save to MongoDB
        Message.save_message(mongo, session['user_id'], sender_name, content) 
        
        # 2. Broadcast message to all connected clients
        timestamp = datetime.datetime.utcnow().strftime('%H:%M') 
        emit('new_message', {
            'sender': sender_name,
            'content': content,
            'time': timestamp
        }, room='global_chat', broadcast=True)

# --- Start Server ---
# Final entry point for WSGI server compatibility
if __name__ == '__main__':
    print("Attempting to connect to MongoDB and start Flask/SocketIO server...")
    # Note: In production, the host's server (like Passenger/Gunicorn) handles the start.
    # This block is mainly for local testing now.
    app.run(debug=True)