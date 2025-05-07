import argparse
import sys
import base64
import requests
import time
import os
import cv2
import numpy as np
import threading
from threading import Lock

from functools import lru_cache

from picamera2 import MappedArray, Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import (NetworkIntrinsics,
                                      postprocess_nanodet_detection)
from picamera2.previews.qt import QGlPicamera2

from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, 
                            QLineEdit, QHBoxLayout, QComboBox)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject, QThread, pyqtSlot

from ApiWorkers import TimeInWorker, TimeOutWorker
                   
last_results = None
results_lock = Lock()
global last_detections


# Add these global variables
class FaceSignals(QObject):
    status_update = pyqtSignal(str)
    input_toggle = pyqtSignal(bool)
    show_message = pyqtSignal(str)

face_signals = FaceSignals()


def parse_detections(metadata: dict):
    """Parse the output tensor into a number of detected objects, scaled to the ISP output."""
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


# Modified draw_detections function
def draw_detections(request):
    """Draw the detections for this request onto the ISP output."""
    global current_frame
    with results_lock:
        detections = last_results
        current_frame = request
        
    if not detections:
        face_signals.status_update.emit("Waiting for face...")
        return

    face_count = len(detections)
    
    if face_count == 0:
        print("Here")
        face_signals.status_update.emit("Waiting for face...")
    elif face_count > 1:
        face_signals.status_update.emit("Multiple faces detected!")
        face_signals.input_toggle.emit(False)
    else:
        face_signals.status_update.emit("Ready for RFID input")
        face_signals.input_toggle.emit(True)

    # Rest of drawing logic...
    labels = get_labels()
    with MappedArray(request, 'main') as m:
        for detection in detections:
            x, y, w, h = detection.box
            label = f"{labels[int(detection.category)]} ({detection.conf:.2f})"

            # # Calculate text size and position
            # (text_width, text_height), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            # text_x = x + 5
            # text_y = y + 15

            # Create a copy of the array to draw the background with opacity
            overlay = m.array.copy()

            # # Draw the background rectangle on the overlay
            # cv2.rectangle(overlay,
                          # (text_x, text_y - text_height),
                          # (text_x + text_width, text_y + baseline),
                          # (255, 255, 255),  # Background color (white)
                          # cv2.FILLED)

            alpha = 0.30
            cv2.addWeighted(overlay, alpha, m.array, 1 - alpha, 0, m.array)

            # # Draw text on top of the background
            # cv2.putText(m.array, label, (text_x, text_y),
                        # cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

            # Draw detection box
            cv2.rectangle(m.array, (x - 15, y - 15), (x + w + 15, y + h + 15), (0, 255, 0, 0), thickness=2)

        if intrinsics.preserve_aspect_ratio:
            b_x, b_y, b_w, b_h = imx500.get_roi_scaled(request)
            color = (255, 0, 0)  # red
            cv2.putText(m.array, "ROI", (b_x + 5, b_y + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            cv2.rectangle(m.array, (b_x, b_y), (b_x + b_w, b_y + b_h), (255, 0, 0, 0))


class Detection:
    def __init__(self, coords, category, conf, metadata):
        """Create a Detection object, recording the bounding box, category and confidence."""
        self.category = category
        self.conf = conf
        self.box = imx500.convert_inference_coords(coords, metadata, picam2)

class RawCaptureWorker(QThread):
    frame_ready = pyqtSignal(np.ndarray)
    
    def __init__(self, picam2):
        super().__init__()
        self.picam2 = picam2
        
    def run(self):
        frame = self.picam2.capture_array("main")
        print(frame.shape)
        self.frame_ready.emit(frame)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        # for managing parallel API calls…
        self.api_workers = []
        self._pending_calls = 0
        self._any_match = False
        self._matched_name = ""
        self._matched_time = ""
        self.api_type = "Time In"
        self._raw_capture_worker = RawCaptureWorker(picam2)
        self._raw_capture_worker.frame_ready.connect(self._on_raw_frame)
        
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        
        #Header
        header = QLabel("UP-Tap Attendance System")
        header.setStyleSheet("font-size: 18px; font-weight: bold;")
        header.setAlignment(Qt.AlignCenter)
        desc = QLabel("Scan your RFID card while looking straight into the camera for face verification")
        layout.addWidget(header)
        layout.addWidget(desc)
        
        # Camera preview
        self.preview = QGlPicamera2(picam2, width=640, height=480, keep_ar=True)
        self.preview.setFixedSize(640, 480)
        self.preview.setStyleSheet("background-color: black; border-radius: 8px;")
        layout.addWidget(self.preview)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 18px; background-color: #f1f1f1; border: 1px solid #ddd; padding: 10px; border-radius: 6px;")
        layout.addWidget(self.status_label)

        apiType = QComboBox()
        apiType.addItems(['Time In', 'Time Out'])
        layout.addWidget(apiType)
        apiType.currentTextChanged.connect(self.on_api_type_change)
        
        # RFID input
        input_layout = QHBoxLayout()
        self.rfid_input = QLineEdit()
        self.rfid_input.setPlaceholderText("Tap your UP RFID to the scanner...")
        self.rfid_input.setEnabled(False)
        self.rfid_input.setMaxLength(10)
        input_layout.addWidget(QLabel("RFID:"))
        input_layout.addWidget(self.rfid_input)
    
        layout.addLayout(input_layout)
        
        # Message label
        self.message_label = QLabel()
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setStyleSheet("font-size: 14px; color: #666;")
        layout.addWidget(self.message_label)
        
        self.setLayout(layout)
        
        # Connect signals
        face_signals.status_update.connect(self.update_status)
        face_signals.input_toggle.connect(self.toggle_input)
        face_signals.show_message.connect(self.show_message)
        self.rfid_input.returnPressed.connect(self.handle_rfid)
        
        
    def update_status(self, text):
        self.status_label.setText(text)
        
    def toggle_input(self, enabled):
        self.rfid_input.setEnabled(enabled)
        if enabled:
            self.rfid_input.setFocus()
            
    def show_message(self, text):
        self.message_label.setText(text)
        QTimer.singleShot(3000, lambda: self.message_label.setText(""))

    def on_api_type_change(self, s: str):
        self.api_type = s
        
    @pyqtSlot(int, bool, str, str, str)
    def handle_timein_response(self, idx, success, message, student_name, time_in):
        # drop finished threads
        self.api_workers = [w for w in self.api_workers if w.isRunning()]

        if success and not self._any_match:
            # capture first successful match
            self._any_match = True
            self._matched_name = student_name
            self._matched_time = time_in

        self._pending_calls -= 1

        # once all have returned…
        if self._pending_calls == 0:
            if self._any_match:
                face_signals.show_message.emit(
                    f"Time‑in recorded for {self._matched_name} at {self._matched_time}"
                )
            else:
                face_signals.show_message.emit(
                    f"Face not verified: {message}"
                )
    @pyqtSlot(int, bool, str, str, str)
    def handle_timeout_response(self, idx, success, message, student_name, time_out):
        # drop finished threads
        self.api_workers = [w for w in self.api_workers if w.isRunning()]

        if success and not self._any_match:
            # capture first successful match
            self._any_match = True
            self._matched_name = student_name
            self._matched_time = time_out

        self._pending_calls -= 1

        # once all have returned…
        if self._pending_calls == 0:
            if self._any_match:
                face_signals.show_message.emit(
                    f"Time‑out recorded for {self._matched_name} at {self._matched_time}"
                )
            else:
                face_signals.show_message.emit(
                    f"Face not verified: {message}"
                )

    def handle_rfid(self):
        rfid = self.rfid_input.text()
        if len(rfid) != 10 or not rfid.isdigit():
            self.show_message("Invalid RFID - must be 10 digits!")
            return
            
        self.rfid_input.clear()
        self.toggle_input(False)
        self.send_face_data(rfid) 
        
    def _on_raw_frame(self, raw_frame):
        face_detections = [d for d in last_results if d.category == 0][:5]
        if not face_detections:
            return
        # Reset our aggregate state
        self._pending_calls = len(face_detections)
        self._any_match = False
        self._matched_name = ""
        self._matched_time = ""

        for idx, det in enumerate(face_detections):
            x, y, w, h = det.box
            face_img = raw_frame[y:y+h, x:x+w]
            corrected = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
            ok, buf = cv2.imencode('.jpg', face_img)
            if not ok:
                self._pending_calls -= 1
                continue

            b64 = base64.b64encode(buf).decode('utf-8')
            if self.api_type == 'Time In':
                worker = TimeInWorker(idx, self._pending_rfid, b64)
                worker.finished.connect(self.handle_timein_response)
            elif self.api_type == 'Time Out':
                worker = TimeOutWorker(idx, self._pending_rfid, b64)
                worker.finished.connect(self.handle_timeout_response)
                
            worker.start()
            self.api_workers.append(worker)
            # (optional) save locally
            # self.save_image_local(f"{self._pending_rfid}_{idx}", face_img)
    
    def send_face_data(self, rfid_text):
        self._pending_rfid = rfid_text
        self._raw_capture_worker.start()

        face_detections = [d for d in last_results if d.category == 0][:5]
        if not face_detections:
            return

        # # Reset our aggregate state
        # self._pending_calls = len(face_detections)
        # self._any_match = False
        # self._matched_name = ""
        # self._matched_time = ""

        # # Grab one copy of the frame buffer
        # # with MappedArray(current_frame, 'main') as m:
            # # frame = m.array.copy()

        # # for idx, det in enumerate(face_detections):
            # # x, y, w, h = det.box
            # # face_img = frame[y: y+h, x: x+w]
        # for idx, det in enumerate(face_detections):
            # x, y, w, h = det.box
            # face_img = raw_frame[y:y+h, x:x+w]
            # ok, buf = cv2.imencode('.png', face_img)
            # if not ok:
                # self._pending_calls -= 1
                # continue

            # b64 = base64.b64encode(buf).decode('utf-8')
            # worker = TimeInWorker(idx, student_id, b64)
            # worker.finished.connect(self.handle_timein_response)
            # worker.start()
            # self.api_workers.append(worker)
            # # (optional) save locally
            # self.save_image_local(f"{student_id}_{idx}", face_img)
         
    def save_image_local(self, rfid, image):
        os.makedirs("captures", exist_ok=True)
        filename = f"captures/{rfid}_{int(time.time())}.jpg"
        cv2.imwrite(filename, image)

    def handle_api_response(self, success, message):
        # Clean up finished workers
        self.api_workers = [w for w in self.api_workers if w.isRunning()]
        self.show_message(message)

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, help="Path of the model",
                        default="/home/UPtap/Desktop/UP-Tap/model/yolo_face_detect/model_imx_model/rpk_output/network.rpk")
    parser.add_argument("--fps", type=int, help="Frames per second", default=60)
    parser.add_argument("--bbox-normalization", action=argparse.BooleanOptionalAction, help="Normalize bbox", default=True)
    parser.add_argument("--bbox-order", choices=["yx", "xy"], default="xy",
                        help="Set bbox order yx -> (y0, x0, y1, x1) xy -> (x0, y0, x1, y1)")
    parser.add_argument("--threshold", type=float, default=0.55, help="Detection threshold")
    parser.add_argument("--iou", type=float, default=0.65, help="Set iou threshold")
    parser.add_argument("--max-detections", type=int, default=10, help="Set max detections")
    parser.add_argument("--ignore-dash-labels", action=argparse.BooleanOptionalAction, help="Remove '-' labels ")
    parser.add_argument("--postprocess", choices=["", "nanodet"],
                        default=None, help="Run post process of type")
    parser.add_argument("-r", "--preserve-aspect-ratio", action=argparse.BooleanOptionalAction,
                        help="preserve the pixel aspect ratio of the input tensor")
    parser.add_argument("--labels", type=str, default="/home/UPtap/Desktop/UP-Tap/model/yolo_face_detect/model_imx_model/labels.txt",
                        help="Path to the labels file")
    parser.add_argument("--print-intrinsics", action="store_true",
                        help="Print JSON network_intrinsics then exit")
    return parser.parse_args()


if __name__ == "__main__":
    last_detections = []
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
    config = picam2.create_preview_configuration(main={"format": "XRGB888", "size": (1920, 1080)}, lores={"format": "XRGB888"}, controls={"FrameRate": intrinsics.inference_rate}, buffer_count=12)

    imx500.show_network_fw_progress_bar()

    #picam2.start(config, show_preview=True)

    # if intrinsics.preserve_aspect_ratio:
        # imx500.set_auto_aspect_ratio()

    
    app = QApplication([])
    main_window = MainWindow()
    main_window.setWindowTitle("UP-Tap")

    last_results = None
    picam2.pre_callback = draw_detections

    def detections_loop():
        global last_results
        while True:
            # Get fresh metadata from a captured frame
            request = picam2.capture_request()
            metadata = request.get_metadata()
            request.release()
            
            # Process and update results atomically
            with results_lock:
                global last_results
                last_results = parse_detections(metadata)
    thread = threading.Thread(target=detections_loop, daemon=True)
    thread.start()
    
    picam2.start()
    main_window.show()
    app.exec()
    
