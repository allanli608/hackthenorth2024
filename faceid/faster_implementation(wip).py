import cv2
import os
from deepface import DeepFace
import numpy as np


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
                model_name='VGG-Face',
                distance_metric='cosine',
                enforce_detection=True,
                threshold=threshold,
                silent=True,
            )

            if results and isinstance(results, list) and len(results) > 0:
                # Get the first dataframe from results
                result_df = results[0]

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
live_verification(db_path='./raw_data', threshold=0.6)
