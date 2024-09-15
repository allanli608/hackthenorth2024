import json
from webbrowser import get
from flask import Flask, request, jsonify, g
from flask_cors import CORS
from utils import generate_unique_id
import sqlite3
import os
from werkzeug.utils import secure_filename

DATABASE = 'sample.db'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'  # Make sure this folder exists
app.config['ALLOWED_EXTENSIONS'] = {'mp4', 'quicktime'}
CORS(app)

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


@app.route('/create-event', methods=['POST'])
def create_event():
    eventId = generate_unique_id()
    data = request.json
    email = data.get('email')
    name = data.get('eventName')
    date = data.get('eventDate')
    location = data.get('eventLocation')
    startTime = data.get('eventStartTime')
    endTime = data.get('eventEndTime')

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO events (hostEmail, eventId, name, date, location, startTime, endTime) VALUES (?, ?, ?, ?, ?, ?, ?)", (email, eventId, name, date, location, startTime, endTime))
    db.commit()

    return jsonify({'message': 'Event created successfully!', 'eventId': eventId}), 201


@app.route('/event/<eventId>', methods=['GET'])
def get_event(eventId):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "SELECT name, location, date, startTime, endTime FROM events WHERE eventId = (?)", (eventId,))
    event = cursor.fetchone()

    return jsonify(event), 200


@app.route('/event/<eventId>/start', methods=['POST'])
def start_event():
    print('Starting event')
    # run CV and all that here

    return jsonify({"message": "Successfully ran event"}), 200


@app.route('/event/<eventId>/guests', methods=['GET'])
def get_guests(eventId):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM guests WHERE eventId = (?)", (eventId,))
    guests = cursor.fetchall()

    return jsonify(guests), 200


@app.route('/events', methods=['GET'])
def get_events():
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM events WHERE hostEmail = (?)",
                   (request.args.get('email'),))
    events = cursor.fetchall()

    return jsonify(events), 200


@app.route('/register-guest', methods=['POST'])
def register_event():
    data = json.loads(request.form.get('guestData'))
    name = data.get('guestName')
    email = data.get('guestEmail')
    eventId = data.get('eventId')
    file = request.files['guestVideo']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    filename = ''
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        "INSERT INTO guests (eventId, name, email, videoName) VALUES (?, ?, ?, ?)", (eventId, name, email, filename))
    db.commit()

    return jsonify({'message': 'Guest registered successfully!'}), 201


if __name__ == '__main__':
    # Initialize the database before starting the server
    init_db()
    app.run(host='0.0.0.0', debug=True)
