from deepface import DeepFace  # Ensure DeepFace is installed and imported
import cv2
import os
from deepface import DeepFace
import numpy as np
import glob
import pandas as pd
import random
import base64
import requests
import json
from datetime import datetime, timedelta

import serial
import time
import collections

# Open the serial connection (adjust the port as needed)
ser = serial.Serial('COM9', 9600, timeout=1)

# Allow some time for the connection to establish
time.sleep(2)

print('connected:', ser)


def sendAttackSignal():
    # Send a message to the Arduino
    ser.write(b'1')
    time.sleep(6)
    ser.write(b'0')


# Parameters
CONFIDENCE_THRESHOLD = 0.4  # Minimum confidence to trigger servo
FRAME_WINDOW_SIZE = 30  # Number of frames to consider for rolling confidence
DECAY_RATE = 0.1  # Rate to decrease confidence when no detection occurs

# Create a deque to track detection confidence
confidence_window = collections.deque(maxlen=FRAME_WINDOW_SIZE)

# Global Event ID
EVENT_ID = 12345  # Replace with the actual event ID

# Dictionary to track the last time a POST request was sent for each person
last_sent_times = {}

# Cooldown period (30 seconds)
COOLDOWN_PERIOD = timedelta(seconds=30)


def extract_frames_from_mp4(mp4_file, num_frames=1):
    # Ensure the output directory is the same as the MP4 file directory
    output_dir = os.path.dirname(mp4_file)

    # Open the specified video file
    cap = cv2.VideoCapture(mp4_file)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if frame_count == 0:
        print(f"Error: {mp4_file} contains no frames.")
        return []

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
                        print(f"Frame {frame_num} verified and saved at {
                              img_path}.")
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
    return frame_images  # Return the file paths of saved images


# Function to convert image to base64 format


def encode_image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)
    encoded_string = base64.b64encode(buffer).decode('utf-8')
    return encoded_string


# Function to send POST request
def send_user_event(name, event_id, image, time):
    # Replace with actual API endpoint
    url = "http://localhost:5000/log-attendee"

    # Prepare data payload
    data = {
        "name": name,
        "event_id": event_id,
        "time": time,
        "image": image
    }
    print(f"Sending POST request: {data}")
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"Successfully sent user data for {name}")
        else:
            print(f"Failed to send user data: {response.status_code}")
    except Exception as e:
        print(f"Error during sending POST request: {e}")


def live_verification(db_path, threshold=0.4):
    confidence_score = 0

    cap = cv2.VideoCapture(
        "rtsp://clbwng:hackthenorth@10.37.102.137:554/stream1")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        try:
            # Use DeepFace.find to get the most likely matches
            results = DeepFace.find(
                img_path=rgb_frame,
                db_path=db_path,
                distance_metric='cosine',
                enforce_detection=False,  # Avoid error if no face is detected
                silent=True
            )

            detected = False  # To check if "caleb" is recognized
            if results and isinstance(results, list) and len(results) > 0:
                for result_df in results:
                    if not result_df.empty:
                        for idx, row in result_df.iterrows():
                            person_name = os.path.basename(
                                row['identity']).split('_')[0]
                            distance = row['distance']
                            x, y, w, h = int(row['source_x']), int(
                                row['source_y']), int(row['source_w']), int(row['source_h'])

                            if distance < threshold:
                                label = f"{person_name} (Dist: {distance:.2f})"
                                color = (0, 255, 0)  # Green for recognized
                                if person_name == "caleb":
                                    detected = True
                                    # Mark this frame as positive detection
                                    confidence_window.append(1)
                                else:
                                    confidence_window.append(0)  # Not Caleb

                                # Capture the current time and encode the image
                                current_time = datetime.now()

                                # Check if the last POST request was sent over 30 seconds ago
                                if person_name not in last_sent_times or \
                                        current_time - last_sent_times[person_name] > COOLDOWN_PERIOD:

                                    # Encode the image
                                    encoded_image = encode_image_to_base64(
                                        frame)

                                    # Send POST request with user info
                                    send_user_event(
                                        name=person_name,
                                        event_id=EVENT_ID,
                                        image=encoded_image,
                                        time=current_time.strftime(
                                            "%Y-%m-%d %H:%M:%S")
                                    )

                                    # Update the last sent time for the person
                                    last_sent_times[person_name] = current_time

                                # Draw bounding box and label
                                cv2.rectangle(
                                    frame, (x, y), (x + w, y + h), color, 2)
                                cv2.putText(frame, label, (x, y - 10),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2, cv2.LINE_AA)
                            else:
                                confidence_window.append(0)

            # Decay confidence if no detection
            if not detected:
                confidence_score = max(0, confidence_score - DECAY_RATE)

            # Calculate the rolling confidence score
            if confidence_window:
                confidence_score = sum(confidence_window) / \
                    len(confidence_window)

            # Trigger servo if confidence exceeds threshold
            if confidence_score >= CONFIDENCE_THRESHOLD:
                print("Caleb detected with high confidence, sending attack signal.")
                sendAttackSignal()  # Trigger servo
                confidence_window.clear()  # Reset after triggering

        except Exception as e:
            print(f"Error during face recognition: {e}")

        cv2.imshow('Face Recognition', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


# Example usage
live_verification(db_path='.\\raw_data', threshold=0.3)
