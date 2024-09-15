import cv2
import os
from deepface import DeepFace
import numpy as np
import random
import glob


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
                            img1_path=img_path, img2_path=img_path)
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


def live_verification(db_path, threshold=0.4):
    # Initialize video capture (webcam)
    cap = cv2.VideoCapture(0)

    # Setup face database
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Convert BGR (OpenCV format) to RGB (DeepFace expected format)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        try:
            # Use DeepFace.find to get the most likely matches
            results = DeepFace.find(
                img_path=rgb_frame,
                db_path=db_path,
                model_name='Facenet512',
                distance_metric='cosine',
                enforce_detection=False,  # Set to False to avoid error if no face is detected
                threshold=threshold,
                silent=True
            )

            if results and isinstance(results, list) and len(results) > 0:
                # Get the first dataframe from results
                result_df = results[0]
                print(result_df)
                if not result_df.empty:
                    # Sort results by distance (lower is better)
                    best_match = result_df.loc[result_df['distance'].idxmin()]
                    distance = best_match['distance']

                    if distance < threshold:
                        name = best_match['identity']
                        text = f'{name} recognized (Distance: {distance:.2f})'
                        color = (0, 255, 0)  # Green for recognized
                    else:
                        text = "Unknown"
                        color = (128, 128, 128)  # Grey for unknown
                else:
                    text = "Unknown"
                    color = (128, 128, 128)  # Grey for unknown
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


# Example usage
live_verification(db_path='.\\raw_data', threshold=0.6)


# Example usage
# extract_frames_from_mp4(mp4_dir='.\\sample_mp4s', output_dir='.\\raw_data', num_frames=10)
