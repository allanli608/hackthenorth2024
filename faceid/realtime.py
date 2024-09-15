import cv2
import torch
import joblib
import numpy as np
from facenet_pytorch import MTCNN, InceptionResnetV1

# Load the trained SVM model and label encoder
svm_model = joblib.load('svm_face_recognition_model.pkl')
label_encoder = joblib.load('label_encoder.pkl')

# Initialize MTCNN for face detection and InceptionResnetV1 for face embeddings
mtcnn = MTCNN(keep_all=False, device='cpu')
resnet = InceptionResnetV1(pretrained='vggface2').eval()

# Function to predict face using the trained SVM model


def predict_face(embedding, threshold=0.5):
    # Predict the probability of each class
    probs = svm_model.predict_proba(embedding)

    # Get the class with the highest probability
    max_prob = np.max(probs)
    pred_class = np.argmax(probs)

    # If the highest probability is below the threshold, classify as 'Unknown'
    if max_prob < threshold:
        return 'Unknown', max_prob
    else:
        # Return the predicted class label
        pred_label = label_encoder.inverse_transform([pred_class])[0]
        return pred_label, max_prob

# Function to run real-time face detection and recognition


def run_realtime_face_recognition(threshold=0.5):
    # Open webcam
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame from webcam")
            break

        # Convert frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Detect faces
        boxes, probs = mtcnn.detect(frame_rgb)

        if boxes is not None:
            for i, box in enumerate(boxes):
                if probs[i] > 0.95:  # Confidence threshold for face detection
                    # Draw the bounding box
                    box = [int(b) for b in box]
                    cropped_face = frame_rgb[box[1]:box[3], box[0]:box[2]]

                    # Preprocess the face for embedding
                    cropped_face = cv2.resize(cropped_face, (160, 160))
                    cropped_face = torch.from_numpy(cropped_face).permute(
                        2, 0, 1).unsqueeze(0).float()

                    # Generate embedding
                    with torch.no_grad():
                        embedding = resnet(cropped_face).cpu().numpy()

                    # Predict using SVM model
                    pred_label, confidence = predict_face(embedding, threshold)

                    # Draw the bounding box with the appropriate color
                    if pred_label == 'Unknown':
                        color = (0, 0, 255)  # Red for unknown
                    else:
                        color = (0, 255, 0)  # Green for recognized face

                    # Draw the bounding box and label
                    cv2.rectangle(
                        frame, (box[0], box[1]), (box[2], box[3]), color, 2)
                    cv2.putText(frame, f'{pred_label} ({confidence:.2f})',
                                (box[0], box[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
                else:
                    # If face detection confidence is low, skip
                    continue

        # Display the frame
        cv2.imshow('Real-Time Face Recognition', frame)

        # Break loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    run_realtime_face_recognition(threshold=0.5)
