import os
import cv2
import dlib
import numpy as np
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path

# Flask setup
app = Flask(__name__)
CORS(app)

# Directories
UPLOAD_FOLDER = 'uploads'
KNOWN_FACES_FOLDER = 'known_faces'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(KNOWN_FACES_FOLDER, exist_ok=True)

# Load dlib models
pose_predictor = dlib.shape_predictor("pretrained_model/shape_predictor_68_face_landmarks.dat")
face_encoder = dlib.face_recognition_model_v1("pretrained_model/dlib_face_recognition_resnet_model_v1.dat")
face_detector = dlib.get_frontal_face_detector()

# Spring Boot API details
SPRING_BOOT_URL = "http://localhost:1010/admin/user-images"
SPRING_BOOT_LOGIN_URL = "http://localhost:1010/auth/login-faceid"
def get_face_encoding(image):
    """Detect face in the image and return its encoding."""
    detections = face_detector(image, 1)
    if len(detections) == 0:
        return None
    shape = pose_predictor(image, detections[0])
    encoding = face_encoder.compute_face_descriptor(image, shape)
    return np.array(encoding)

def fetch_and_save_known_faces_from_spring():
    """Fetch known faces and emails from Spring Boot API and save images to known_faces folder."""
    known_encodings = []
    known_emails = []

    try:
        # Fetch user image paths and emails from Spring Boot
        response = requests.get(SPRING_BOOT_URL)
        response.raise_for_status()
        data = response.json()

        if data.get("statusCode") == 200 and "data" in data:
            user_images = data["data"]
            base_url = "http://localhost:1010/uploads/image/"

            for user_data in user_images:
                image_path = user_data.get("image")
                email = user_data.get("email")

                if not image_path or not email:
                    continue

                # Extract filename from the full path
                filename = os.path.basename(image_path)
                image_url = f"{base_url}{filename}"

                # Download the image
                img_response = requests.get(image_url, stream=True)
                img_response.raise_for_status()

                # Save the image to the known_faces folder
                save_path = os.path.join(KNOWN_FACES_FOLDER, filename)
                with open(save_path, 'wb') as f:
                    f.write(img_response.content)

                # Load the saved image for encoding
                image = cv2.imread(save_path)
                if image is None:
                    continue
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Get face encoding
                encoding = get_face_encoding(image)
                if encoding is not None:
                    known_encodings.append(encoding)
                    known_emails.append(email)

    except Exception as e:
        print(f"Error fetching and saving known faces: {e}")

    return known_encodings, known_emails

def login_user_via_faceid(email):
    """Call Spring Boot API to log in the user using their email."""
    try:
        response = requests.post(SPRING_BOOT_LOGIN_URL, json={"email": email})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error logging in user via FaceID: {e}")
        return None

# Load known faces at startup
# known_encodings, known_emails = fetch_and_save_known_faces_from_spring()
# print(f"{len(known_encodings)} known face(s) loaded from Spring Boot and saved to known_faces.")

@app.route('/upload', methods=['POST'])
def upload_video():
    """Handle video upload and face recognition."""
    if 'video' not in request.files:
        return jsonify({'message': 'No video file provided'}), 400
    known_encodings, known_emails = fetch_and_save_known_faces_from_spring()
    print(f"{len(known_encodings)} known face(s) loaded from Spring Boot and saved to known_faces.")

    video = request.files['video']
    video_path = os.path.join(UPLOAD_FOLDER, video.filename)
    video.save(video_path)
    
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        return jsonify({'message': 'Error opening video file'}), 400
    
    tolerance = 0.6  # Adjust as needed
    recognized_email = None
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        detections = face_detector(rgb_frame, 1)
        
        for detection in detections:
            shape = pose_predictor(rgb_frame, detection)
            face_encoding = np.array(face_encoder.compute_face_descriptor(rgb_frame, shape))
            
            for known_encoding, email in zip(known_encodings, known_emails):
                distance = np.linalg.norm(known_encoding - face_encoding)
                if distance <= tolerance:
                    recognized_email = email
                    break
        
        if recognized_email:
            break  # Stop processing once a known face is found
    
    video_capture.release()
    os.remove(video_path)  # Clean up uploaded file
    
    if recognized_email:
        # Log in the user via FaceID
        login_response = login_user_via_faceid(recognized_email)
        if login_response:
            return jsonify({
                'message': 'User logged in successfully',
                'email': recognized_email,
                'login_response': login_response
            })
        else:
            return jsonify({'message': 'Failed to log in user'}), 500
    else:
        return jsonify({'message': 'No recognized face found'}), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)