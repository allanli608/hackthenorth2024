import cv2
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import time

# Initialize MTCNN for face detection
mtcnn = MTCNN(keep_all=True, device='cpu')

# Load pre-trained Inception ResNet model
resnet = InceptionResnetV1(pretrained='vggface2').eval()


def capture_face(probability_threshold=0.95):
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture frame")
            continue

        # Convert frame to RGB (MTCNN expects RGB images)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect face
        boxes, probs = mtcnn.detect(frame_rgb)

        if boxes is not None and probs is not None:
            for box, prob in zip(boxes, probs):
                if prob > probability_threshold:
                    cap.release()
                    return frame_rgb, box

        # Display the frame
        cv2.imshow('Capturing Face', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return None, None


def extract_face(img, box):
    # Ensure box coordinates are integers
    box = box.astype(int)
    face = img[box[1]:box[3], box[0]:box[2]]
    face = cv2.resize(face, (160, 160))
    face = torch.from_numpy(face).permute(2, 0, 1).float()
    return face.unsqueeze(0)


def compare_faces(face1, face2):
    with torch.no_grad():
        emb1 = resnet(face1)
        emb2 = resnet(face2)

    distance = (emb1 - emb2).norm().item()
    similarity = 1 / (1 + distance)
    return similarity


# Stage 1: Register user
print("Stage 1: Registering user. Please look at the camera.")
registered_frame, registered_box = capture_face()

if registered_frame is None:
    print("Failed to register user. Exiting.")
    exit()

registered_face = extract_face(registered_frame, registered_box)
print("User registered successfully.")

# Stage 2: Verification
print("Stage 2: Preparing for verification.")
time.sleep(5)
print("Now accepting trials. Please look at the camera.")

while True:
    trial_frame, trial_box = capture_face()

    if trial_frame is None:
        print("No face detected. Try again.")
        continue

    trial_face = extract_face(trial_frame, trial_box)
    similarity = compare_faces(registered_face, trial_face)

    if similarity > 0.7:  # You can adjust this threshold
        print(f"Face match! Similarity: {similarity:.2f}")
    else:
        print(f"No match. Similarity: {similarity:.2f}")

    choice = input("Try again? (y/n): ")
    if choice.lower() != 'y':
        break

print("Face recognition process completed.")
