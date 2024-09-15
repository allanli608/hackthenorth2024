import cv2
import numpy as np
import time
from deepface import DeepFace

# Initialize face detector
face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml")


def extract_face(img, box):
    if box is None:
        return None
    face = img[box[1]:box[1]+box[3], box[0]:box[0]+box[2]]
    if face.size == 0:
        return None
    face = cv2.resize(face, (224, 224))
    return face


def compare_faces(face1, face2):
    if face1 is None or face2 is None:
        return 0
    try:
        result = DeepFace.verify(face1, face2, enforce_detection=False)
        return result['distance']
    except:
        return 0


def register_face():
    cap = cv2.VideoCapture(
        "rtsp://clbwng:hackthenorth@10.37.102.137:554/stream1")
    registered_face = None
    high_confidence_start_time = None
    registration_duration = 1  # seconds

    print("Registering user. Please look at the camera.")
    print("The box will turn green when a suitable face is detected.")
    print("Registration will complete after 5 seconds of continuous high-confidence detection.")

    while registered_face is None:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        frame_with_box = frame.copy()

        if len(faces) > 1:
            print("Please show only 1 face")
            high_confidence_start_time = None
        elif len(faces) == 1:
            (x, y, w, h) = faces[0]
            cv2.rectangle(frame_with_box, (x, y), (x+w, y+h), (0, 255, 0), 2)

            if high_confidence_start_time is None:
                high_confidence_start_time = time.time()
            elif time.time() - high_confidence_start_time >= registration_duration:
                registered_face = extract_face(frame, (x, y, w, h))
                if registered_face is not None:
                    print("Registration successful!")
                else:
                    print("Registration failed. Please try again.")
                    high_confidence_start_time = None
        else:
            high_confidence_start_time = None

        # Display countdown if in high confidence state
        if high_confidence_start_time is not None:
            elapsed_time = time.time() - high_confidence_start_time
            remaining_time = max(0, registration_duration - elapsed_time)
            cv2.putText(frame_with_box, f"Registering in: {remaining_time:.1f}s", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        cv2.imshow('Face Registration', frame_with_box)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return registered_face


def real_time_verification(registered_face):
    cap = cv2.VideoCapture(
        "rtsp://clbwng:hackthenorth@10.37.102.137:554/stream1")

    print("Real-time verification started. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_detector.detectMultiScale(gray, 1.3, 5)

        frame_with_box = frame.copy()

        if len(faces) == 0:
            cv2.putText(frame_with_box, "No face detected", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        else:
            for (x, y, w, h) in faces:
                detected_face = extract_face(frame, (x, y, w, h))
                if detected_face is not None:
                    similarity = compare_faces(registered_face, detected_face)

                    color = (0, 255, 0) if similarity < 0.6 else (0, 0, 255)
                    cv2.rectangle(frame_with_box, (x, y), (x+w, y+h), color, 2)
                    cv2.putText(frame_with_box, f"Distance: {similarity:.2f}", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                else:
                    cv2.putText(frame_with_box, "Face extraction failed", (x, y - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)

        cv2.imshow('Real-time Face Verification', frame_with_box)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Main execution
registered_face = register_face()
if registered_face is not None:
    print("User registered successfully.")
    real_time_verification(registered_face)
else:
    print("Failed to register user. Exiting.")

print("Face recognition process completed.")
