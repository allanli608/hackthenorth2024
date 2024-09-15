import cv2
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
import numpy as np
import os
import glob
import os
from sklearn import svm
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import joblib
# Initialize MTCNN for face detection and landmark prediction
mtcnn = MTCNN(keep_all=True, device='cpu', post_process=False)

# Load pre-trained Inception ResNet model
resnet = InceptionResnetV1(pretrained='vggface2').eval()

# Function to segment video and process frames


def process_video(video_path, output_dir):
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = int(cap.get(cv2.CAP_PROP_FPS))

    segment_size = total_frames // 100  # Divide into 100 parts

    embeddings_list = []  # List to store embeddings

    for i in range(100):
        # Frame at the end of each segment
        target_frame = (i + 1) * segment_size - 1

        # Set video to the target frame
        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
        ret, frame = cap.read()

        if not ret:
            print(f"Failed to read frame {target_frame} in {video_path}")
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        boxes, probs, landmarks = mtcnn.detect(frame_rgb, landmarks=True)

        # If no face or multiple faces, skip this frame
        if boxes is None or len(boxes) != 1:
            print(f"Skipping frame {
                  target_frame} due to no or multiple faces.")
            continue

        box, prob, landmark = boxes[0], probs[0], landmarks[0]

        if prob > 0.95:
            print(f"Face detected in frame {target_frame}, processing...")
            cropped_face = extract_face(frame_rgb, box, landmark)
            if cropped_face is not None:
                with torch.no_grad():
                    embedding = resnet(cropped_face).cpu().numpy()
                embeddings_list.append(embedding)
            else:
                print(f"Failed to extract face from frame {target_frame}.")
        else:
            print(f"Low confidence for face detection in frame {
                  target_frame}.")

    cap.release()

    # Save embeddings for this video
    if len(embeddings_list) > 0:
        embeddings_array = np.array(embeddings_list)
        video_name = os.path.basename(video_path).split('.')[0]
        np.save(os.path.join(output_dir, f"{
                video_name}_embeddings.npy"), embeddings_array)
        print(f"Embeddings saved for {video_name}.")
    else:
        print(f"No embeddings extracted for {video_path}.")

# Function to extract face and align it


def extract_face(img, box, landmarks):
    if box is None or landmarks is None:
        return None
    box = box.astype(int)
    face = img[box[1]:box[3], box[0]:box[2]]
    if face.size == 0:
        return None

    aligned_face = align_face(face, landmarks)
    aligned_face = cv2.resize(aligned_face, (160, 160))
    aligned_face = torch.from_numpy(aligned_face).permute(2, 0, 1).float()
    return aligned_face.unsqueeze(0)

# Align face based on eye landmarks


def align_face(face, landmarks):
    left_eye, right_eye = landmarks[0], landmarks[1]
    dx, dy = right_eye[0] - left_eye[0], right_eye[1] - left_eye[1]
    angle = np.degrees(np.arctan2(dy, dx))  # Calculate angle between the eyes

    eyes_center = ((left_eye[0] + right_eye[0]) // 2,
                   (left_eye[1] + right_eye[1]) // 2)
    M = cv2.getRotationMatrix2D(eyes_center, angle, 1)

    aligned_face = cv2.warpAffine(
        face, M, (face.shape[1], face.shape[0]), flags=cv2.INTER_CUBIC)
    return aligned_face

# Main function to find videos and process them


def main(input_dir, output_dir):
    # Ensure output directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Find all *.mp4 files
    video_files = glob.glob(os.path.join(input_dir, '*.mp4'))

    # Process each video file
    for video_file in video_files:
        print(f"Processing video: {video_file}")
        process_video(video_file, output_dir)
        print(f"Completed processing: {video_file}")

    print("All videos processed.")

# Load all the embeddings and corresponding labels (from file names)


def load_embeddings_and_labels(embedding_dir):
    embeddings = []
    labels = []

    for filename in os.listdir(embedding_dir):
        if filename.endswith('.npy'):
            # Load the embeddings from each file
            embedding = np.load(os.path.join(embedding_dir, filename))
            print(f"Loaded {filename} with shape {
                  embedding.shape}")  # Check the shape

            # The label is the filename without extension
            label = os.path.splitext(filename)[0]

            # If embedding is 3D, flatten it to 2D
            if len(embedding.shape) == 3:
                embedding = embedding.reshape(embedding.shape[0], -1)

            # Append embeddings and replicate the label for each embedding
            embeddings.append(embedding)
            # Replicate the label for each embedding
            labels.extend([label] * embedding.shape[0])

    # Convert lists to numpy arrays
    embeddings = np.concatenate(embeddings, axis=0)
    labels = np.array(labels)

    return embeddings, labels
# Train the SVM model


def train_svm(embedding_dir):
    # Load the embeddings and labels
    embeddings, labels = load_embeddings_and_labels(embedding_dir)

    # Encode the labels to integer format
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(labels)

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        embeddings, y, test_size=0.2, random_state=42)

    # Create the SVM model pipeline (with scaling)
    clf = make_pipeline(StandardScaler(), svm.SVC(
        kernel='linear', probability=True))

    # Train the model
    clf.fit(X_train, y_train)

    # Evaluate the model
    y_pred = clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"Model accuracy: {accuracy * 100:.2f}%")

    # Save the model and label encoder
    joblib.dump(clf, 'svm_face_recognition_model.pkl')
    joblib.dump(label_encoder, 'label_encoder.pkl')

# Function to predict the name of a face with an unknown threshold


def predict_face(embedding, threshold=0.5):
    # Load the trained model and label encoder
    clf = joblib.load('svm_face_recognition_model.pkl')
    label_encoder = joblib.load('label_encoder.pkl')

    # Predict probabilities for each class
    probs = clf.predict_proba(embedding)

    # Get the class with the highest probability
    max_prob = np.max(probs)
    pred_class = np.argmax(probs)

    # If the highest probability is below the threshold, classify as 'unknown'
    if max_prob < threshold:
        return 'Unknown', max_prob
    else:
        # Otherwise, return the predicted class label
        pred_label = label_encoder.inverse_transform([pred_class])[0]
        return pred_label, max_prob


# Run the script
if __name__ == "__main__":
    input_directory = './data'  # Directory where .mp4 files are located
    output_directory = './embeddings'  # Directory to save embeddings

    # main(input_directory, output_directory)
    embedding_directory = 'embeddings/'  # Directory where embeddings are stored
    train_svm(embedding_directory)
