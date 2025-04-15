import argparse
import sys
import base64
import threading
import requests
from functools import lru_cache
import cv2
import numpy as np
# from picamera2 import MappedArray, Picamera2
# from picamera2.devices import IMX500
# from picamera2.devices.imx500 import (NetworkIntrinsics, postprocess_nanodet_detection)
import tkinter as tk
from tkinter import ttk
from ttkbootstrap import Style
from PIL import Image, ImageTk


# Global variables for sharing between threads
last_detections = []
latest_frame = None
latest_detections = None
frame_lock = threading.Lock()
global img_number
img_number = 1

class RFIDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("UP-Tap RFID Attendance System")
        self.style = Style(theme="cosmo")  # Modern theme

        # Main Frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # RFID Input Label
        self.label = ttk.Label(self.main_frame, text="RFID Input:", font=("Helvetica", 14))
        self.label.pack(pady=10)

        # RFID Input Entry
        self.entry = ttk.Entry(self.main_frame, font=("Helvetica", 14), width=20)
        self.entry.pack(pady=10)

        # Submit Button
        self.submit_button = ttk.Button(self.main_frame, text="Submit", command=self.submit_rfid)
        self.submit_button.pack(pady=10)

        # Status Label
        self.status_label = ttk.Label(self.main_frame, text="", font=("Helvetica", 12))
        self.status_label.pack(pady=10)

    def submit_rfid(self):
        user_input = self.entry.get().strip()
        if len(user_input) == 10 and user_input.isdigit():
            self.status_label.config(text=f"Valid RFID input received: {user_input}", foreground="green")
            self.process_rfid(user_input)
        else:
            self.status_label.config(text="Invalid RFID input", foreground="red")

    def process_rfid(self, user_input):
        # Get frame and detections in thread-safe manner
        with frame_lock:
            current_frame = latest_frame.copy() if latest_frame is not None else None
            current_detections = latest_detections.copy() if latest_detections else None

        if current_detections is None or current_frame is None or len(current_detections) == 0 or len(current_frame) == 0:
            self.status_label.config(text="No recent detections available", foreground="red")
            return

        # Get first detection and crop image
        detection = current_detections[0]
        x, y, w, h = detection.box

        if w <= 0 or h <= 0:
            self.status_label.config(text="Invalid detection dimensions", foreground="red")
            return

        global img_number
        img_number += 1
        cropped = current_frame[y:y+h, x:x+w]
        cv2.imwrite(f"cropped_detection_{detection.category}_{img_number}.jpg", cropped)

        # Convert to base64
        _, buffer = cv2.imencode('.jpg', cropped)
        image_base64 = base64.b64encode(buffer).decode('utf-8')

        # Send in background thread
        def send_request():
            try:
                response = requests.post(
                    "http://192.168.1.1:8000/api/attendance/time-in/",
                    json={
                        "student_id": user_input,
                        "subject_id": 0,
                        "face_data": image_base64,
                    },
                    headers={
                        "Authorization" : "Bearer ee3d0e2717367127246001d2f2c0510a07116260",
                        "Content-Type": "application/json"
                    },
                    timeout=5
                )
                self.status_label.config(text=f"POST successful: {response.status_code}", foreground="green")
            except Exception as e:
                self.status_label.config(text=f"POST failed: {str(e)}", foreground="red")

        threading.Thread(target=send_request, daemon=True).start()


# Start the Tkinter UI
root = tk.Tk()
app = RFIDApp(root)
root.mainloop()