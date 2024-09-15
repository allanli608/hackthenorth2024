import cv2
import torch
from facenet_pytorch import InceptionResnetV1
import numpy as np
import time
from scipy.spatial import distance as dist
from mtcnn.mtcnn import MTCNN


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


def capture_face_embeddings(cap, num_photos=10, delay=0.2):
    embeddings = []
    for _ in range(num_photos):
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes, probs, landmarks = mtcnn.detect(frame_rgb, landmarks=True)

        if boxes is not None and len(boxes) == 1:
            box, prob, landmark = boxes[0], probs[0], landmarks[0]
            if prob > 0.95:
                detected_face = extract_face(frame_rgb, box, landmark)
                if detected_face is not None:
                    with torch.no_grad():
                        embedding = resnet(detected_face).cpu().numpy()
                    embeddings.append(embedding)

        time.sleep(delay)  # Wait for the specified delay

    return embeddings


def register_face(list_name):
    cap = cv2.VideoCapture(0)
    registered_embeddings = []
    angles = ['center', 'left', 'right']  # List of angles
    current_angle = 0

    print(f"Registering user for {list_name}. Please look at the camera.")
    print("Turn your head slightly for each angle as prompted.")

    while current_angle < len(angles):
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes, probs, landmarks = mtcnn.detect(frame_rgb, landmarks=True)

        frame_with_box = frame.copy()

        if boxes is not None and len(boxes) == 1:
            box, prob, landmark = boxes[0], probs[0], landmarks[0]
            if prob > 0.95:
                cv2.rectangle(frame_with_box, (int(box[0]), int(
                    box[1])), (int(box[2]), int(box[3])), (0, 255, 0), 2)
                cv2.putText(frame_with_box, f"Score: {prob:.2f}", (int(box[0]), int(box[1]) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                print(f"Please face {angles[current_angle]}")
                embeddings = capture_face_embeddings(cap)

                if embeddings:
                    # Compute the average embedding for the current angle
                    avg_embedding = np.mean(embeddings, axis=0)
                    registered_embeddings.append(avg_embedding)
                    print(f"{angles[current_angle]
                             } face captured successfully!")
                    current_angle += 1  # Move to the next angle after success
                else:
                    print("No valid face detected. Please try again.")
            else:
                print("Low confidence in face detection. Please try again.")
        else:
            print("No face detected. Please try again.")

        cv2.imshow(f'Face Registration - {list_name}', frame_with_box)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

    return registered_embeddings


def compare_faces(registered_embeddings, face_to_compare):
    if face_to_compare is None:
        return []
    with torch.no_grad():
        emb_to_compare = resnet(face_to_compare).cpu().numpy()
    similarities = []
    for reg_emb in registered_embeddings:
        similarity = np.dot(emb_to_compare.flatten(), reg_emb.flatten(
        )) / (np.linalg.norm(emb_to_compare) * np.linalg.norm(reg_emb))
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
    if eye_nose_ratio > 0.5 and eye_nose_ratio < 1:  # Arbitrary range for head movement
        return True
    return False


def real_time_verification(whitelist_embeddings, blacklist_embeddings):
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
                        similarities_whitelist = compare_faces(
                            whitelist_embeddings, detected_face)
                        similarities_blacklist = compare_faces(
                            blacklist_embeddings, detected_face)
                        avg_similarity_whitelist = np.mean(
                            similarities_whitelist) if similarities_whitelist else 0
                        avg_similarity_blacklist = np.mean(
                            similarities_blacklist) if similarities_blacklist else 0

                        if avg_similarity_whitelist > 0.7:
                            color = (0, 255, 0)  # Green for whitelist
                        elif avg_similarity_blacklist > 0.7:
                            color = (0, 0, 255)  # Red for blacklist
                        else:
                            color = (128, 128, 128)  # Grey for neither

                        cv2.rectangle(frame_with_box, (int(box[0]), int(
                            box[1])), (int(box[2]), int(box[3])), color, 2)
                        cv2.putText(frame_with_box, f"Avg: {avg_similarity_whitelist:.2f}", (10, 30),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                        cv2.putText(frame_with_box, "Whitelist" if avg_similarity_whitelist > 0.7 else "Blacklist" if avg_similarity_blacklist > 0.7 else "Unknown", (10, 60),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        cv2.imshow('Real-time Verification', frame_with_box)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def main():
    while True:
        command = input(
            "Enter command (blacklist, whitelist, verification, quit): ").strip().lower()

        if command == 'blacklist':
            print(
                "Registering blacklist faces. Please follow the instructions on the screen.")
            blacklist_embeddings = register_face('blacklist')
            print("Blacklist registration completed.")
        elif command == 'whitelist':
            print(
                "Registering whitelist faces. Please follow the instructions on the screen.")
            whitelist_embeddings = register_face('whitelist')
            print("Whitelist registration completed.")
        elif command == 'verification':
            print(
                "Starting verification. Ensure you have registered faces for whitelist and blacklist.")
            real_time_verification(whitelist_embeddings, blacklist_embeddings)
        elif command == 'quit':
            print("Exiting the application.")
            break
        else:
            print(
                "Invalid command. Please enter 'blacklist', 'whitelist', 'verification', or 'quit'.")


if __name__ == "__main__":
    whitelist_embeddings = []
    blacklist_embeddings = []
    main()
