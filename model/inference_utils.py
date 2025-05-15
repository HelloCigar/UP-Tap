import io
import base64
from PIL import Image
import numpy as np
import tensorflow.lite as tflite
import cv2
import mediapipe as mp

# Initialize MediaPipe Face Detection and Face Mesh
mp_face_detection = mp.solutions.face_detection
mp_face_mesh = mp.solutions.face_mesh
face_detection = mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True)

# Load TFLite MobileFaceNet
interpreter = tflite.Interpreter(model_path="model/output_model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

def base64_to_image(base64_string):
    if base64_string.startswith("data:"):
        header, base64_data = base64_string.split(",", 1)
    else:
        base64_data = base64_string    
    image_data = base64.b64decode(base64_data)
    image = Image.open(io.BytesIO(image_data))
    return image

# Function to detect and crop a face using MediaPipe
def detect_and_crop_face(image_string: str):
    img = base64_to_image(image_string)
    image_np = np.array(img.convert('RGB'))
    results = face_detection.process(image_np)

    if not results.detections:
        return None  # No face detected

    # Get bounding box of the first detected face
    detection = results.detections[0]
    bboxC = detection.location_data.relative_bounding_box
    ih, iw, _ = image_np.shape
    x = int(bboxC.xmin * iw)
    y = int(bboxC.ymin * ih)
    w = int(bboxC.width * iw)
    h = int(bboxC.height * ih)

    # Ensure the bounding box is within image bounds
    x = max(0, x)
    y = max(0, y)
    x2 = min(iw, x + w)
    y2 = min(ih, y + h)

    return img.crop((x, y, x2, y2))

# Function to preprocess a face for MobileFaceNet
def preprocess_face(face):
    face = face.convert("RGB")
    face = face.resize((112, 112))
    face = np.array(face).astype(np.float32) / 255.0
    return np.expand_dims(face, axis=0)

# Function to compute face embeddings
def compute_embedding(face):
    face = preprocess_face(face)
    interpreter.set_tensor(input_details[0]['index'], face)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index']).flatten()

def align_face(image_string: str):
    img = base64_to_image(image_string)
    if img is None:
        return None  # No face detected

    image = np.array(img.convert('RGB'))
    h, w = image.shape[:2]
    rgb = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    results = face_mesh.process(rgb)

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        left_eye = np.array([landmarks[33].x * w, landmarks[33].y * h])
        right_eye = np.array([landmarks[263].x * w, landmarks[263].y * h])

        # Calculate angle
        dx = right_eye[0] - left_eye[0]
        dy = right_eye[1] - left_eye[1]
        angle = np.degrees(np.arctan2(dy, dx))

        # Center between eyes
        center = tuple(((left_eye + right_eye) / 2).astype(int))

        # Rotate image using PIL
        aligned_pil = img.rotate(angle, center=center, resample=Image.BILINEAR)

        x_coords = [lm.x * w for lm in landmarks]
        y_coords = [lm.y * h for lm in landmarks]
        x_min, x_max = int(min(x_coords)), int(max(x_coords))
        y_min, y_max = int(min(y_coords)), int(max(y_coords))

        # Crop the aligned image
        face_crop = aligned_pil.crop((x_min, y_min, x_max, y_max))
        return face_crop

    return img  # return original if no face landmarks found
