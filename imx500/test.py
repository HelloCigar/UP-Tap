import argparse
import sys
import base64
import threading
import requests
from functools import lru_cache
import cv2
import numpy as np
from picamera2 import MappedArray, Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import (NetworkIntrinsics,
                                      postprocess_nanodet_detection)

# Global variables for sharing between threads
last_detections = []
latest_frame = None
latest_detections = None
frame_lock = threading.Lock()
global img_number
img_number = 1


class Detection:
    def __init__(self, coords, category, conf, metadata):
        self.category = category
        self.conf = conf
        self.box = imx500.convert_inference_coords(coords, metadata, picam2)

def parse_detections(metadata: dict):
    global last_detections

    bbox_normalization = intrinsics.bbox_normalization
    bbox_order = intrinsics.bbox_order
    threshold = args.threshold
    iou = args.iou
    max_detections = args.max_detections

    np_outputs = imx500.get_outputs(metadata, add_batch=True)
    input_w, input_h = imx500.get_input_size()
    if np_outputs is None:
        return last_detections
    if intrinsics.postprocess == "nanodet":
        boxes, scores, classes = \
            postprocess_nanodet_detection(outputs=np_outputs[0], conf=threshold, iou_thres=iou,
                                          max_out_dets=max_detections)[0]
        from picamera2.devices.imx500.postprocess import scale_boxes
        boxes = scale_boxes(boxes, 1, 1, input_h, input_w, False, False)
    else:
        boxes, scores, classes = np_outputs[0][0], np_outputs[1][0], np_outputs[2][0]
        if bbox_normalization:
            boxes = boxes / input_h

        if bbox_order == "xy":
            boxes = boxes[:, [1, 0, 3, 2]]
        boxes = np.array_split(boxes, 4, axis=1)
        boxes = zip(*boxes)

    last_detections = [
        Detection(box, category, score, metadata)
        for box, score, category in zip(boxes, scores, classes)
        if score > threshold
    ]
    return last_detections



@lru_cache
def get_labels():
    labels = intrinsics.labels

    if intrinsics.ignore_dash_labels:
        labels = [label for label in labels if label and label != "-"]
    return labels



def draw_detections(request, stream="main"):
    global latest_frame, latest_detections
    detections = last_results
    if detections is None:
        return
    labels = get_labels()
    with MappedArray(request, stream) as m:
        for detection in detections:
            x, y, w, h = detection.box
            label = f"{labels[int(detection.category)]} ({detection.conf:.2f})"

            # Calculate text size and position
            (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            text_x = x + 5
            text_y = y + 15

            # Create a copy of the array to draw the background with opacity
            overlay = m.array.copy()

            # Draw the background rectangle on the overlay
            cv2.rectangle(overlay,
                          (text_x, text_y - text_height),
                          (text_x + text_width, text_y + baseline),
                          (255, 255, 255),  # Background color (white)
                          cv2.FILLED)

            alpha = 0.30
            cv2.addWeighted(overlay, alpha, m.array, 1 - alpha, 0, m.array)

            # Draw text on top of the background
            cv2.putText(m.array, label, (text_x, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            # Draw detection box
            cv2.rectangle(m.array, (x, y), (x + w, y + h), (0, 255, 0, 0), thickness=2)

        if intrinsics.preserve_aspect_ratio:
            b_x, b_y, b_w, b_h = imx500.get_roi_scaled(request)
            color = (255, 0, 0)  # red
            cv2.putText(m.array, "ROI", (b_x + 5, b_y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            cv2.rectangle(m.array, (b_x, b_y), (b_x + b_w, b_y + b_h), (255, 0, 0, 0))
            
        with frame_lock:
            latest_frame = m.array.copy()
            latest_detections = detections.copy() if detections else None

def input_thread_function():
    while True:
        # Read from HID device (RFID reader)
        user_input = input().strip()
        
        if len(user_input) == 10 and user_input.isdigit():
            print(f"Valid RFID input received: {user_input}")
            
            # Get frame and detections in thread-safe manner
            with frame_lock:
                current_frame = latest_frame.copy() if latest_frame is not None else None
                current_detections = latest_detections.copy() if latest_detections else None
            print(current_detections)
            if current_detections is None or current_frame is None or len(current_detections) == 0 or len(current_frame) == 0:
                print("No recent detections available")
                continue
                
            # Get first detection and crop image
            detection = current_detections[0]
            x, y, w, h = detection.box
            
            
            if w <= 0 or h <= 0:
                print("Invalid detection dimensions")
                continue
            
            img_number =+1
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
                    print(f"POST successful: {response.status_code}")
                except Exception as e:
                    print(f"POST failed: {str(e)}")
            
            threading.Thread(target=send_request, daemon=True).start()

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, help="Path of the model",
                        default="/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk")
    parser.add_argument("--fps", type=int, help="Frames per second")
    parser.add_argument("--bbox-normalization", action=argparse.BooleanOptionalAction, help="Normalize bbox")
    parser.add_argument("--bbox-order", choices=["yx", "xy"], default="yx",
                        help="Set bbox order yx -> (y0, x0, y1, x1) xy -> (x0, y0, x1, y1)")
    parser.add_argument("--threshold", type=float, default=0.70, help="Detection threshold")
    parser.add_argument("--iou", type=float, default=0.65, help="Set iou threshold")
    parser.add_argument("--max-detections", type=int, default=1, help="Set max detections")
    parser.add_argument("--ignore-dash-labels", action=argparse.BooleanOptionalAction, help="Remove '-' labels ")
    parser.add_argument("--postprocess", choices=["", "nanodet"],
                        default=None, help="Run post process of type")
    parser.add_argument("-r", "--preserve-aspect-ratio", action=argparse.BooleanOptionalAction,
                        help="preserve the pixel aspect ratio of the input tensor")
    parser.add_argument("--labels", type=str,
                        help="Path to the labels file")
    parser.add_argument("--print-intrinsics", action="store_true",
                        help="Print JSON network_intrinsics then exit")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    
    # This must be called before instantiation of Picamera2
    imx500 = IMX500(args.model)
    intrinsics = imx500.network_intrinsics
    if not intrinsics:
        intrinsics = NetworkIntrinsics()
        intrinsics.task = "object detection"
    elif intrinsics.task != "object detection":
        print("Network is not an object detection task", file=sys.stderr)
        exit()

    # Override intrinsics from args
    for key, value in vars(args).items():
        if key == 'labels' and value is not None:
            with open(value, 'r') as f:
                intrinsics.labels = f.read().splitlines()
        elif hasattr(intrinsics, key) and value is not None:
            setattr(intrinsics, key, value)

    # Defaults
    if intrinsics.labels is None:
        with open("assets/coco_labels.txt", "r") as f:
            intrinsics.labels = f.read().splitlines()
    intrinsics.update_with_defaults()

    if args.print_intrinsics:
        print(intrinsics)
        exit()

    picam2 = Picamera2(imx500.camera_num)
    config = picam2.create_preview_configuration(controls={"FrameRate": intrinsics.inference_rate}, buffer_count=12)

    imx500.show_network_fw_progress_bar()
    picam2.start(config, show_preview=True)

    if intrinsics.preserve_aspect_ratio:
        imx500.set_auto_aspect_ratio()
    
    input_thread = threading.Thread(target=input_thread_function, daemon=True)
    input_thread.start()

    last_results = None
    picam2.pre_callback = draw_detections
    while True:
        last_results = parse_detections(picam2.capture_metadata())
