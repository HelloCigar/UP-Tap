import os
import base64
import cv2
import numpy as np
from deepface import DeepFace
from ninja import Schema
base_path = os.getcwd()
folder_path = base_path + "/captured/"

if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    
def base64_to_bgr(base64_img):

    str_cleaned = base64_img.split(",")[1]

    # Decode the base64 string to bytes
    img_data = base64.b64decode(str_cleaned)
    
    # Convert bytes data to numpy array
    np_arr = np.frombuffer(img_data, np.uint8)
    
    # Decode the numpy array to an image
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    return img  # This is in BGR format


class Img64Schema(Schema):
    img64_str: str
