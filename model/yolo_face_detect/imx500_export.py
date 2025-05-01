from huggingface_hub import hf_hub_download
from ultralytics import YOLO
                

# Load YOLOv8 face detection model
model_path = hf_hub_download(repo_id="arnabdhar/YOLOv8-Face-Detection", filename="model.pt")
face_detector = YOLO(model_path)

face_detector.export(format="imx")  # exports with PTQ quantization by default
