import cv2
import glob
import os
from deepface import DeepFace
import random
import pandas as pd
import base64
import numpy as np
from io import BytesIO
from PIL import Image


def extract_frames_from_mp4(mp4_dir, output_dir, num_frames=1):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    mp4_files = glob.glob(os.path.join(mp4_dir, '*.mp4'))

    for mp4_file in mp4_files:
        cap = cv2.VideoCapture(mp4_file)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        # Randomly select frame indices
        frame_indices = random.sample(range(frame_count), num_frames)

        basename = os.path.basename(mp4_file)
        name, _ = os.path.splitext(basename)

        valid_frames = 0
        frame_images = []

        while valid_frames < num_frames:
            for frame_num in frame_indices:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
                ret, frame = cap.read()

                if ret:
                    img_path = os.path.join(
                        output_dir, f'{name}_frame{frame_num}.jpg')
                    cv2.imwrite(img_path, frame)

                    # Verify the frame with DeepFace
                    try:
                        result = DeepFace.verify(
                            img1_path=img_path, img2_path=img_path, detector_backend="mtcnn", model_name="Facenet512")
                        if result['verified']:
                            valid_frames += 1
                            frame_images.append(img_path)
                            print(f"Frame {frame_num} verified and saved.")
                        else:
                            print(f"Frame {frame_num} not verified, deleting {
                                  img_path}.")
                            os.remove(img_path)  # Delete unverified frame

                        if valid_frames >= num_frames:
                            break
                    except Exception as e:
                        print(f"Error verifying frame {frame_num}: {e}")
                        # Delete the frame if verification fails due to an error
                        if os.path.exists(img_path):
                            os.remove(img_path)
                        continue

            # If not enough valid frames, select more random frames
            if valid_frames < num_frames:
                frame_indices = random.sample(range(frame_count), num_frames)

        cap.release()


def live_verification(known_images_dir, threshold=0.4):
    # Initialize video capture (webcam)
    cap = cv2.VideoCapture(0)

    # Load known images as NumPy arrays
    known_images = {}
    for filename in os.listdir(known_images_dir):
        if filename.endswith(('.jpg', '.png')):
            img_path = os.path.join(known_images_dir, filename)
            img = cv2.imread(img_path)
            known_images[filename] = img

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert BGR (OpenCV format) to RGB (DeepFace expected format)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        verification_results = []

        try:
            # Verify against all images in known_images
            for filename, known_image in known_images.items():
                # Convert known_image to RGB
                rgb_known_image = cv2.cvtColor(known_image, cv2.COLOR_BGR2RGB)

                result = DeepFace.verify(
                    img1_path=rgb_frame, img2_path=rgb_known_image, enforce_detection=False
                )
                distance = result['distance']
                verification_results.append({
                    'image': filename,
                    'distance': distance
                })

            # Sort results by distance (lower is better)
            sorted_results = sorted(
                verification_results, key=lambda x: x['distance'])

            # Take the best match
            best_match = sorted_results[0] if sorted_results else None

            if best_match and best_match['distance'] < threshold:
                name = os.path.basename(best_match['image']).split('_')[0]
                text = f'{name} recognized (Distance: {
                    best_match["distance"]:.2f})'
                color = (0, 255, 0)  # Green for recognized
            else:
                text = "Unknown"
                color = (128, 128, 128)  # Grey for unknown

        except Exception as e:
            print(f"Error during face recognition: {e}")
            text = "Unknown"
            color = (128, 128, 128)  # Grey for unknown

        # Display results on the frame
        h, w, _ = frame.shape
        cv2.putText(frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX,
                    1, color, 2, cv2.LINE_AA)
        cv2.imshow('Face Recognition', frame)

        # Exit loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# extract_frames_from_mp4(
   # mp4_dir='./data', output_dir='./raw_data', num_frames=1)
# Run live verification
live_verification(known_images_dir='.\\raw_data', threshold=0.6)
