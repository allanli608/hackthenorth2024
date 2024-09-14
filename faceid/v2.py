import cv2
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import numpy as np
import time

# Initialize MTCNN for face detection
mtcnn = MTCNN(keep_all=True, device='cpu')

# Load pre-trained Inception ResNet model
resnet = InceptionResnetV1(pretrained='vggface2').eval()


def extract_face(img, box):
    if box is None:
        return None
    box = box.astype(int)
    face = img[box[1]:box[3], box[0]:box[2]]
    if face.size == 0:
        return None
    face = cv2.resize(face, (160, 160))
    face = torch.from_numpy(face).permute(2, 0, 1).float()
    return face.unsqueeze(0)


def compare_faces(face1, face2):
    if face1 is None or face2 is None:
        return 0
    with torch.no_grad():
        emb1 = resnet(face1)
        emb2 = resnet(face2)
    distance = (emb1 - emb2).norm().item()
    similarity = 1 / (1 + distance)
    return similarity


def register_face():
    cap = cv2.VideoCapture(0)
    registered_face = None
    high_confidence_start_time = None
    registration_duration = 5  # seconds

    print("Registering user. Please look at the camera.")
    print("The box will turn green when a suitable face is detected.")
    print("Registration will complete after 5 seconds of continuous high-confidence detection.")

    while registered_face is None:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes, probs = mtcnn.detect(frame_rgb)

        frame_with_box = frame.copy()

        if boxes is not None and len(boxes) > 1:
            print("Please show only 1 face")
            high_confidence_start_time = None
        elif boxes is not None and len(boxes) == 1:
            box, prob = boxes[0], probs[0]
            if prob > 0.95:
                box = box.astype(int)
                cv2.rectangle(
                    frame_with_box, (box[0], box[1]), (box[2], box[3]), (0, 255, 0), 2)
                cv2.putText(frame_with_box, f"Score: {prob:.2f}", (box[0], box[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                if high_confidence_start_time is None:
                    high_confidence_start_time = time.time()
                elif time.time() - high_confidence_start_time >= registration_duration:
                    registered_face = extract_face(frame_rgb, box)
                    if registered_face is not None:
                        print("Registration successful!")
                    else:
                        print("Registration failed. Please try again.")
                        high_confidence_start_time = None
            else:
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
    cap = cv2.VideoCapture(0)

    print("Real-time verification started. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes, probs = mtcnn.detect(frame_rgb)

        frame_with_box = frame.copy()

        if boxes is None or len(boxes) == 0:
            cv2.putText(frame_with_box, "No face detected", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        else:
            for box, prob in zip(boxes, probs):
                if prob > 0.9:  # Only show high-confidence detections
                    box = box.astype(int)
                    detected_face = extract_face(frame_rgb, box)
                    if detected_face is not None:
                        similarity = compare_faces(
                            registered_face, detected_face)

                        color = (0, 255, 0) if similarity > 0.7 else (
                            0, 0, 255)
                        cv2.rectangle(
                            frame_with_box, (box[0], box[1]), (box[2], box[3]), color, 2)
                        cv2.putText(frame_with_box, f"Similarity: {similarity:.2f}", (box[0], box[1] - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                    else:
                        cv2.putText(frame_with_box, "Face extraction failed", (box[0], box[1] - 10),
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
