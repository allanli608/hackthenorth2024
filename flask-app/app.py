import json
from webbrowser import get
from flask import Flask, request, jsonify, g, render_template
from flask_cors import CORS
from utils import generate_unique_id
import sqlite3
import os
from werkzeug.utils import secure_filename
import threading
from face_detection import live_verification, extract_frames_from_mp4
import datetime
from moviepy.editor import VideoFileClip


DATABASE = 'sample.db'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Make sure this folder exists
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'quicktime'}
CORS(app)

# function to start the face id verification


def convert_mov_to_mp4(file_path):
    # Check if the file has a .mov extension
    if not file_path.lower().endswith('.mov'):
        raise ValueError("The input file must have a .mov extension")

    # Load the .mov video file
    clip = VideoFileClip(file_path)

    # Create the output file path with .mp4 extension
    output_file_path = os.path.splitext(file_path)[0] + '.mp4'

    # Write the output as an .mp4 file
    clip.write_videofile(output_file_path, codec="libx264")

    return output_file_path


def run_face_id():
    live_verification(db_path='.\\uploads', threshold=0.3)


def run_extraction():
    extract_frames_from_mp4()

# Function to get a connection to the SQLite database


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Initialize the database (Run this once to create the table)


def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS events (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            hostEmail TEXT NOT NULL,
                            eventId TEXT NOT NULL,
                            name TEXT NOT NULL,
                            date DATE NOT NULL,
                            location TEXT NOT NULL,
                            startTime TIME NOT NULL,
                            endTime TIME NOT NULL
                          )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS guests (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            eventId TEXT NOT NULL,
                            name TEXT NOT NULL,
                            email TEXT NOT NULL,
                            videoName TEXT NOT NULL
                          )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS entry_log (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            eventId TEXT NOT NULL,
                            guestId TEXT NOT NULL,
                            entryTime TIMESTAMP,
                            exitTime TIMESTAMP 
                          )''')
        db.commit()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/')
def homepage():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM guests")
    # cursor.execute("SELECT * FROM events")
    return jsonify(cursor.fetchall()), 200


@app.route('/start-event', methods=['POST'])
def start_event():
    print('Starting event')
    data = request.json
    event_id = data.get('event_id')
    if not event_id:
        return jsonify({'error': 'Event ID is required'}), 400

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "UPDATE events SET startTime = CURRENT_TIMESTAMP WHERE eventId = ?", (event_id,))
    db.commit()

    face_id_thread = threading.Thread(target=run_face_id)
    face_id_thread.start()

    return jsonify({"message": "Event started successfully!"}), 200


@app.route('/log-attendee', methods=['POST'])
def log_attendee():
    data = request.json  # Assuming the data is sent as JSON
    event_id = data.get('event_id')
    guest_id = data.get('name')  # Assuming 'name' is the guest ID
    entry_time = datetime.now()  # Record the current time for the entry

    db = get_db()
    cursor = db.cursor()

    # Insert the attendee's entry into the entry_log table
    cursor.execute('''
        INSERT INTO entry_log (eventId, guestId, entryTime, exitTime)
        VALUES (?, ?, ?, ?)
    ''', (event_id, guest_id, entry_time, None))

    cursor.commit()
    cursor.close()

    return "Attendee logged successfully", 200


@app.route('/entries')
def show_entries():
    db = get_db()
    cursor = db.cursor()

    # Query to fetch all entries ordered by entryTime (most recent at the top)
    cursor.execute('''
        SELECT * FROM entry_log ORDER BY entryTime DESC
    ''')
    entries = cursor.fetchall()

    cursor.close()

    # Render the template and pass the entries data to it
    return render_template('entries.html', entries=entries)


@app.route('/create-event', methods=['POST'])
def create_event():
    eventId = generate_unique_id()
    data = request.json
    email = data.get('email')
    name = data.get('eventName')
    date = data.get('eventDate')
    location = date.get('eventLocation')
    startTime = data.get('eventStartTime')
    endTime = data.get('eventEndTime')

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO events (hostEmail, eventId, name, date, location, startTime, endTime) VALUES (?, ?, ?, ?, ?, ?, ?)", (email, eventId, name, date, location, startTime, endTime))
    db.commit()

    return jsonify({'message': 'Event created successfully!'}), 201


@app.route('/events', methods=['GET'])
def get_events():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM events WHERE hostEmail = (?)",
                   (request.args.get('email'),))
    events = cursor.fetchall()

    return jsonify(events), 200


@app.route('/register-guest/<eventId>', methods=['POST'])
def register_event(eventId):
    data = json.loads(request.form.get('guestData'))
    name = data.get('guestName')
    email = data.get('guestEmail')
    file = request.files['guestVideo']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = ''
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        convert_mov_to_mp4(file_path)
        extract_frames_from_mp4(file_path, 15)
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO guests (eventId, name, email, videoName) VALUES (?, ?, ?, ?)", (eventId, name, email, filename))
    db.commit()

    return jsonify({'message': 'Guest registered successfully!'}), 201


if __name__ == '__main__':
    # Initialize the database before starting the server
    init_db()
    app.run(host='0.0.0.0', debug=False)
