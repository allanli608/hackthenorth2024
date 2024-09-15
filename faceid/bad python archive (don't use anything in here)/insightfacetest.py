import cv2
import numpy as np
import pickle
from deepface import DeepFace
from scipy.spatial.distance import cosine
import time

# Constants
REGISTERED_USERS_FILE = 'user_embeddings.pkl'
BLACKLIST_FILE = 'blacklist_embeddings.pkl'
THRESHOLD = 0.6  # Adjust this based on your needs
FACE_DETECTION_TIME = 2  # Time (in seconds) to wait for a steady face
PHOTO_INTERVAL = 1  # Interval (in seconds) between photos

# Initialize face detector
face_cascade = cv2.CascadeClassifier(
    cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def detect_face(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return faces


def get_face_embedding(image):
    analysis = DeepFace.represent(image, model_name='VGG-Face')
    return analysis[0]['embedding']


def average_embeddings(images):
    embeddings = [get_face_embedding(img) for img in images]
    return np.mean(embeddings, axis=0)


def save_embeddings(filename, embeddings):
    with open(filename, 'wb') as f:
        pickle.dump(embeddings, f)


def load_embeddings(filename):
    try:
        with open(filename, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}


def classify_face(face_embedding, user_embeddings, blacklist_embeddings):
    user_similarities = {user_id: cosine(
        face_embedding, emb) for user_id, emb in user_embeddings.items()}
    blacklist_similarities = {user_id: cosine(
        face_embedding, emb) for user_id, emb in blacklist_embeddings.items()}

    if user_similarities and min(user_similarities.values()) < THRESHOLD:
        return 'whitelist'
    elif blacklist_similarities and min(blacklist_similarities.values()) < THRESHOLD:
        return 'blacklist'
    else:
        return 'neither'


def draw_bbox(frame, face, status, message=None):
    x, y, w, h = face
    color = (0, 255, 0) if status == 'whitelist' else (
        0, 0, 255) if status == 'blacklist' else (128, 128, 128)
    cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
    cv2.putText(frame, status, (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
    if message:
        cv2.putText(
            frame, message, (10, frame.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)


def register_user(user_id):
    cap = cv2.VideoCapture(0)
    images = []
    face_detected_time = None
    face_detected = False
    successful_photos = 0
    total_photos = 5
    print("Please capture 5 different images of the user from different angles.")

    while successful_photos < total_photos:
        ret, frame = cap.read()
        faces = detect_face(frame)

        if len(faces) > 0:
            if not face_detected:
                face_detected_time = time.time()
                face_detected = True
            elif time.time() - face_detected_time >= FACE_DETECTION_TIME:
                x, y, w, h = faces[0]  # Take the first detected face
                face_img = frame[y:y+h, x:x+w]

                try:
                    # Try to get face embedding, if successful add the image
                    face_embedding = get_face_embedding(face_img)
                    if face_embedding is not None:
                        images.append(face_img)
                        successful_photos += 1
                        print(f"Successfully captured photo {
                              successful_photos}/{total_photos}")
                        cv2.imshow("Capture", face_img)
                        time.sleep(PHOTO_INTERVAL)
                except ValueError:
                    print("No face detected in the captured image. Please try again.")

                face_detected = False  # Reset detection to avoid duplicate captures
        else:
            face_detected = False
            draw_bbox(frame, (0, 0, 0, 0), 'no face detected')

        # Display the successful photo count on the frame
        cv2.putText(frame, f"Photos taken: {successful_photos}/{total_photos}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        cv2.imshow("Registration", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    if successful_photos == total_photos:
        user_embedding = average_embeddings(images)
        user_embeddings = load_embeddings(REGISTERED_USERS_FILE)
        user_embeddings[user_id] = user_embedding
        save_embeddings(REGISTERED_USERS_FILE, user_embeddings)
        print(f"User {user_id} registered successfully.")
    else:
        print("Registration failed. Please try again.")


def register_blacklist(user_id):
    cap = cv2.VideoCapture(0)
    images = []
    face_detected_time = None
    face_detected = False
    print("Please capture 5 different images of the person for the blacklist.")

    while len(images) < 5:
        ret, frame = cap.read()
        faces = detect_face(frame)

        if len(faces) > 0:
            if not face_detected:
                face_detected_time = time.time()
                face_detected = True
            elif time.time() - face_detected_time >= FACE_DETECTION_TIME:
                x, y, w, h = faces[0]  # Take the first detected face
                face_img = frame[y:y+h, x:x+w]
                images.append(face_img)
                cv2.imshow("Capture", face_img)
                time.sleep(PHOTO_INTERVAL)
                face_detected = False  # Reset detection to avoid duplicate captures
        else:
            face_detected = False
            draw_bbox(frame, (0, 0, 0, 0), 'no face detected')

        cv2.imshow("Blacklist Registration", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    blacklist_embedding = average_embeddings(images)
    blacklist_embeddings = load_embeddings(BLACKLIST_FILE)
    blacklist_embeddings[user_id] = blacklist_embedding
    save_embeddings(BLACKLIST_FILE, blacklist_embeddings)
    print(f"Blacklist user {user_id} registered successfully.")


def main():
    user_embeddings = load_embeddings(REGISTERED_USERS_FILE)
    blacklist_embeddings = load_embeddings(BLACKLIST_FILE)

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        faces = detect_face(frame)

        if len(faces) == 0:
            draw_bbox(frame, (0, 0, 0, 0), 'no face detected')
        else:
            for (x, y, w, h) in faces:
                face_img = frame[y:y+h, x:x+w]
                face_embedding = get_face_embedding(face_img)
                status = classify_face(
                    face_embedding, user_embeddings, blacklist_embeddings)
                draw_bbox(frame, (x, y, w, h), status)

        cv2.imshow('Face Recognition', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    choice = input(
        "Enter 'register' to register a user or 'blacklist' to blacklist a user or 'start' to start monitoring: ").strip().lower()
    if choice == 'register':
        user_id = input("Enter user ID for registration: ")
        register_user(user_id)
    elif choice == 'blacklist':
        user_id = input("Enter user ID for blacklist: ")
        register_blacklist(user_id)
    elif choice == 'start':
        main()
    else:
        print("Invalid choice.")
