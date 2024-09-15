import cv2
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import numpy as np
import time
from scipy.spatial import distance as dist

# Initialize MTCNN for face detection and landmark prediction
mtcnn = MTCNN(keep_all=True, device='cpu', post_process=False)

# Load pre-trained Inception ResNet model
resnet = InceptionResnetV1(pretrained='vggface2').eval()


def extract_face(img, box, landmarks):
    if box is None or landmarks is None:
        return None
    box = box.astype(int)
    face = img[box[1]:box[3], box[0]:box[2]]
    if face.size == 0:
        return None

    # Align face using eye landmarks
    aligned_face = align_face(face, landmarks)
    aligned_face = cv2.resize(aligned_face, (160, 160))
    aligned_face = torch.from_numpy(aligned_face).permute(2, 0, 1).float()
    return aligned_face.unsqueeze(0)


def align_face(face, landmarks):
    left_eye, right_eye = landmarks[0], landmarks[1]
    dx, dy = right_eye[0] - left_eye[0], right_eye[1] - left_eye[1]
    angle = np.degrees(np.arctan2(dy, dx))  # Calculate angle between the eyes

    # Get center between eyes and rotation matrix
    eyes_center = ((left_eye[0] + right_eye[0]) // 2,
                   (left_eye[1] + right_eye[1]) // 2)
    M = cv2.getRotationMatrix2D(eyes_center, angle, 1)

    # Rotate the face to align the eyes horizontally
    aligned_face = cv2.warpAffine(
        face, M, (face.shape[1], face.shape[0]), flags=cv2.INTER_CUBIC)
    return aligned_face


def compare_faces(registered_embeddings, face_to_compare, threshold=0.7):
    if face_to_compare is None:
        return 0
    with torch.no_grad():
        emb_to_compare = resnet(face_to_compare).cpu()
    similarities = []
    for reg_emb in registered_embeddings:
        similarity = torch.nn.functional.cosine_similarity(
            emb_to_compare, reg_emb).item()
        similarities.append(similarity)
    return similarities


def detect_liveness(landmarks):
    """
    Check head movement by monitoring distance between eyes and nose over frames.
    If head movement is subtle, it's likely a real person.
    """
    left_eye, right_eye, nose = landmarks[0], landmarks[1], landmarks[2]
    eye_dist = dist.euclidean(left_eye, right_eye)
    nose_eye_dist_left = dist.euclidean(nose, left_eye)
    nose_eye_dist_right = dist.euclidean(nose, right_eye)

    # Measure ratio change to detect subtle movements.
    eye_nose_ratio = nose_eye_dist_left / eye_dist
    print(eye_nose_ratio)
    if eye_nose_ratio > 0.5 and eye_nose_ratio < 1:  # Arbitrary range for head movement
        return True
    return False


def register_face():
    cap = cv2.VideoCapture(0)
    registered_embeddings = []
    angles = ['center', 'left', 'right']  # List of angles
    high_confidence_start_time = None
    registration_duration = 5  # seconds
    liveness_detected = False
    current_angle = 0

    print("Registering user. Please look at the camera.")
    print("Turn your head slightly for each angle as prompted.")

    while current_angle < len(angles):
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes, probs, landmarks = mtcnn.detect(frame_rgb, landmarks=True)

        frame_with_box = frame.copy()

        if boxes is not None and len(boxes) > 1:
            print("Please show only 1 face")
            high_confidence_start_time = None
        elif boxes is not None and len(boxes) == 1:
            box, prob, landmark = boxes[0], probs[0], landmarks[0]
            if prob > 0.95:
                cv2.rectangle(frame_with_box, (int(box[0]), int(
                    box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
                cv2.putText(frame_with_box, f"Score: {prob:.2f}", (int(box[0]), int(box[1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # Perform liveness detection (simple head movement)
                if detect_liveness(landmark):
                    liveness_detected = True
                    if high_confidence_start_time is None:
                        high_confidence_start_time = time.time()
                    elif time.time() - high_confidence_start_time >= registration_duration:
                        registered_face = extract_face(
                            frame_rgb, box, landmark)
                        if registered_face is not None:
                            with torch.no_grad():
                                embedding = resnet(registered_face).cpu()
                            registered_embeddings.append(embedding)
                            print(f"{angles[current_angle]
                                     } face captured successfully!")
                            current_angle += 1  # Move to the next angle after success
                            high_confidence_start_time = None
                        else:
                            print("Face extraction failed. Please try again.")
                            high_confidence_start_time = None
                else:
                    liveness_detected = False
                    print("Liveness not detected, please move slightly.")
            else:
                high_confidence_start_time = None
        else:
            high_confidence_start_time = None

        if high_confidence_start_time is not None:
            elapsed_time = time.time() - high_confidence_start_time
            remaining_time = max(0, registration_duration - elapsed_time)
            cv2.putText(frame_with_box, f"Registering in: {remaining_time:.1f}s", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        # Ensure we do not access out of bounds on angles list
        if current_angle < len(angles):
            cv2.putText(frame_with_box, f"Please face {angles[current_angle]}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        cv2.imshow('Face Registration', frame_with_box)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return registered_embeddings


def real_time_verification(registered_embeddings):
    cap = cv2.VideoCapture(0)

    print("Real-time verification started. Press 'q' to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes, probs, landmarks = mtcnn.detect(frame_rgb, landmarks=True)

        frame_with_box = frame.copy()

        if boxes is None or len(boxes) == 0:
            cv2.putText(frame_with_box, "No face detected", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        else:
            for box, prob, landmark in zip(boxes, probs, landmarks):
                if prob > 0.9:  # Only show high-confidence detections
                    detected_face = extract_face(frame_rgb, box, landmark)
                    if detected_face is not None:
                        similarities = compare_faces(
                            registered_embeddings, detected_face)
                        avg_similarity = sum(similarities) / len(similarities)

                        color = (0, 255, 0) if avg_similarity > 0.7 else (
                            0, 0, 255)
                        cv2.rectangle(frame_with_box, (int(box[0]), int(
                            box[1])), (int(box[2]), int(box[3])), color, 2)
                        cv2.putText(frame_with_box, f"Center: {similarities[0]:.2f}", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                        cv2.putText(frame_with_box, f"Left: {similarities[1]:.2f}", (10, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                        cv2.putText(frame_with_box, f"Right: {similarities[2]:.2f}", (10, 90),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                        cv2.putText(frame_with_box, f"Avg: {avg_similarity:.2f}", (10, 120),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                        cv2.putText(frame_with_box, "Match" if avg_similarity > 0.7 else "No Match", (10, 150),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        cv2.imshow('Real-Time Verification', frame_with_box)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Main execution
registered_embeddings = register_face()
if registered_embeddings:
    print("Face registration complete!")
    real_time_verification(registered_embeddings)
else:
    print("No faces registered. Exiting.")
