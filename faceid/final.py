import cv2
import torch
import joblib
import numpy as np
import os
import glob
from facenet_pytorch import MTCNN, InceptionResnetV1
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import make_pipeline

# Initialize MTCNN for face detection and InceptionResnetV1 for face embeddings
mtcnn = MTCNN(keep_all=True, device='cpu', post_process=False)
resnet = InceptionResnetV1(pretrained='vggface2').eval()

# Load the trained Logistic Regression model

# Load label encoder from file


def extract_face(img, box):
    if box is None:
        return None
    box = box.astype(int)

    # Crop the face based on the bounding box provided by MTCNN
    face = img[box[1]:box[3], box[0]:box[2]]
    if face.size == 0:
        return None

    # Resize the face to 160x160 (input size expected by InceptionResnetV1)
    face = cv2.resize(face, (160, 160))

    # Convert the face to the format expected by the model
    face_tensor = torch.from_numpy(face).permute(2, 0, 1).float()
    return face_tensor.unsqueeze(0)

# Function to align face using eye landmarks


def generate_embedding(cropped_face):
    with torch.no_grad():
        embedding = resnet(cropped_face).cpu().numpy()
    return embedding

# Function to predict face using the trained Logistic Regression model


def predict_face(embedding, threshold=0.8):
    # Load the trained model
    clf = joblib.load('logistic_regression_model.pkl')

    # Load label encoder
    label_encoder = joblib.load('label_encoder.pkl')

    # Predict class probabilities
    probas = clf.predict_proba(embedding)
    print(probas)

    # Get the class with the highest probability
    max_proba = np.max(probas, axis=1)
    max_proba_index = np.argmax(probas, axis=1)
    print(max_proba[0])
    # Check if the highest probability exceeds the threshold
    if max_proba[0] > threshold:
        # Get the predicted class
        pred_label = clf.classes_[max_proba_index[0]]
        label_name = label_encoder.inverse_transform([pred_label])[0]
        return label_name
    else:
        return "unknown"


# Function to process videos, extract frames, and save preprocessed face images


def preprocess_videos(video_dir, output_dir='./raw_data'):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    embeddings_dict = {}
    video_paths = glob.glob(os.path.join(video_dir, '*.mp4'))

    for video_path in video_paths:
        print(f"Processing video: {video_path}")
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frames_to_extract = 20
        interval = frame_count // frames_to_extract

        video_filename = os.path.basename(video_path).split('.')[0]
        all_embeddings = []

        for i in range(frames_to_extract):
            frame_number = i * interval
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = cap.read()
            if not ret:
                continue

            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            boxes, probs = mtcnn.detect(img_rgb)

            if boxes is not None:
                for j, box in enumerate(boxes):
                    if probs[j] > 0.95:  # Confidence threshold for face detection
                        cropped_face = extract_face(img_rgb, box)
                        if cropped_face is not None:
                            embedding = generate_embedding(cropped_face)
                            print(embedding)
                            all_embeddings.append(embedding)

                            # Save the cropped face image
                            face_image = cropped_face.squeeze(
                                0).permute(1, 2, 0).numpy()
                            face_image = cv2.cvtColor(
                                face_image, cv2.COLOR_RGB2BGR)
                            img_filename = f"{video_filename}_frame{
                                frame_number}_face{j}.jpg"
                            img_path = os.path.join(output_dir, img_filename)
                            cv2.imwrite(img_path, face_image)

        cap.release()

        if all_embeddings:
            embeddings_array = np.concatenate(all_embeddings, axis=0)
            embeddings_dict[video_filename] = embeddings_array

    return embeddings_dict


# Function to load embeddings and labels from directory


def load_embeddings_and_labels(embedding_dict):
    embeddings, labels = [], []

    for label, emb_array in embedding_dict.items():
        embeddings.append(emb_array)
        labels.extend([label] * emb_array.shape[0])

    embeddings = np.concatenate(embeddings, axis=0)
    labels = np.array(labels)

    # Ensure labels are a 1D array
    if len(labels.shape) > 1:
        labels = labels.ravel()

    return embeddings, labels

# Function to train Logistic Regression model using embeddings


def train_logistic_regression(embedding_dict):
    embeddings, labels = load_embeddings_and_labels(embedding_dict)

    # Reshape embeddings if necessary
    if len(embeddings.shape) == 3:
        embeddings = embeddings.reshape(embeddings.shape[0], -1)

    # Encode labels
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(labels)

    # Ensure labels are a 1D array
    encoded_labels = encoded_labels.ravel()

    # Create a pipeline with standard scaler and logistic regression
    clf = make_pipeline(StandardScaler(), LogisticRegression(
        solver='lbfgs', multi_class='multinomial', max_iter=10000))

    # Perform grid search for hyperparameter tuning
    param_grid = {'logisticregression__C': [
        0.001, 0.01, 0.1, 1, 10, 100, 1000]}
    grid_search = GridSearchCV(clf, param_grid, cv=3)
    grid_search.fit(embeddings, encoded_labels)

    # Save the trained model and label encoder
    joblib.dump(grid_search.best_estimator_, 'logistic_regression_model.pkl')
    joblib.dump(label_encoder, 'label_encoder.pkl')

    print(f"Best parameters found: {grid_search.best_params_}")


def run_realtime_face_recognition():
    cap = cv2.VideoCapture(0)  # Open the webcam

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to capture image")
            break

        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes, probs = mtcnn.detect(img_rgb)

        if boxes is not None:
            for i, box in enumerate(boxes):
                if probs[i] > 0.95:  # Confidence threshold for face detection
                    cropped_face = extract_face(img_rgb, box)
                    if cropped_face is not None:
                        embedding = generate_embedding(cropped_face)
                        label_name = predict_face(embedding)

                        # Draw bounding box and label on the frame
                        box = box.astype(int)
                        color = (0, 255, 0) if label_name != "unknown" else (
                            128, 128, 128)  # Green for recognized, Grey for unknown
                        cv2.rectangle(
                            frame, (box[0], box[1]), (box[2], box[3]), color, 2)
                        cv2.putText(
                            frame, label_name, (box[0], box[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        # Display the resulting frame
        cv2.imshow('Real-Time Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Main function to preprocess videos, extract frames, and train Logistic Regression
if __name__ == "__main__":
    video_directory = './data'  # Directory where MP4 videos are located

    # Process videos and get embeddings dictionary
    embeddings_dict = preprocess_videos(video_directory)

    # Train the Logistic Regression model using the embeddings dictionary
    train_logistic_regression(embeddings_dict)

    # Uncomment to run real-time face recognition
    run_realtime_face_recognition()
