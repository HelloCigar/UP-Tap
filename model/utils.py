import io
import base64
import tensorflow as tf
from PIL import Image
import numpy as np
from huggingface_hub import hf_hub_download
from ultralytics import YOLO
import tensorflow.lite as tflite


# Load YOLOv8 face detection model
model_path = hf_hub_download(repo_id="arnabdhar/YOLOv8-Face-Detection", filename="model.pt")
face_detector = YOLO(model_path)

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

# Function to detect and crop a face
def detect_and_crop_face(image_string: str):
    img = base64_to_image(image_string)
    results = face_detector(img)

    if len(results[0].boxes) == 0:
        return None  # No face detected

    bbox = results[0].boxes.xyxy[0].int().tolist()
    return img.crop(bbox)

# Function to preprocess a face for MobileFaceNet
def preprocess_face(face):
    face = face.convert('RGB')  # Convert to RGB to remove alpha channel if present
    face = face.resize((112, 112))
    face = np.array(face).astype(np.float32) / 255.0
    return np.expand_dims(face, axis=0)

# Function to compute face embeddings
def compute_embedding(face):
    face = preprocess_face(face)
    interpreter.set_tensor(input_details[0]['index'], face)
    interpreter.invoke()
    return interpreter.get_tensor(output_details[0]['index']).flatten()

