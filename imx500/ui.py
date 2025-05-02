import sys
import argparse
import multiprocessing
from functools import lru_cache
from queue import Queue
from enum import Enum
import threading
import atexit
import cv2
import numpy as np
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QThread
from PyQt5.QtWidgets import QApplication
from picamera2 import Picamera2, MappedArray
from picamera2.previews.qt_previews import QtGlPreview
from picamera2.devices import IMX500
from picamera2.devices.imx500 import NetworkIntrinsics, postprocess_nanodet_detection


class DetectionProcessor(QObject):
    detection_ready = pyqtSignal(list, object)  # (detections, metadata)

    def __init__(self, args):
        super().__init__()
        self.args = args
        self.pool = multiprocessing.Pool(processes=4)

    def process_request(self, request):
        metadata = request.get_metadata()
        if metadata:
            async_result = self.pool.apply_async(parse_detections, (metadata,))
            detections = async_result.get()
            self.detection_ready.emit(detections, metadata)
        request.release()

class ApplicationWrapper:
    def __init__(self, args):
        self.args = args
        self.picam2 = None
        self.preview = None
        self.detection_processor = None
        self.overlay = None

    def initialize_camera(self):
        imx500 = IMX500(self.args.model)
        self.picam2 = Picamera2(imx500.camera_num)
        
        # Configure camera
        config = self.picam2.create_preview_configuration()
        self.picam2.configure(config)
        
        # Initialize preview system
        self.preview = QtGlPreview(width=1280, height=720)
        self.preview.start(self.picam2)
        
        # Set up detection processing
        self.detection_processor = DetectionProcessor(self.args)
        self.detection_processor.moveToThread(QThread.currentThread())
        self.detection_processor.detection_ready.connect(self.update_overlay)

    def start_processing(self):
        def capture_loop():
            while True:
                try:
                    request = self.picam2.capture_request()
                    self.detection_processor.process_request(request)
                except Exception as e:
                    print(f"Capture error: {e}")
                    break

        processing_thread = threading.Thread(target=capture_loop)
        processing_thread.daemon = True
        processing_thread.start()

    def update_overlay(self, detections, metadata):
        # Create overlay image with detections
        overlay = np.zeros((720, 1280, 4), dtype=np.uint8)
        
        # Draw detections
        labels = get_labels()
        for detection in detections:
            x, y, w, h = detection.box
            label = f"{labels[int(detection.category)]} ({detection.conf:.2f})"
            
            # Draw bounding box
            cv2.rectangle(overlay, (x, y), (x+w, y+h), (0, 255, 0, 255), 2)
            
            # Draw text
            cv2.putText(overlay, label, (x, y-10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255, 255), 2)

        self.preview.set_overlay(overlay)

    def run(self):
        self.initialize_camera()
        self.picam2.start()
        self.start_processing()
        
        # Start Qt event loop
        QApplication.instance().exec_()

    def cleanup(self):
        self.picam2.stop()
        self.preview.stop()
        self.detection_processor.pool.close()

class Detection:
    def __init__(self, coords, category, conf, metadata):
        self.category = category
        self.conf = conf
        self.box = imx500.convert_inference_coords(coords, metadata, picam2)
 
def parse_detections(metadata: dict):
    bbox_normalization = intrinsics.bbox_normalization
    threshold = args.threshold
    iou = args.iou
    max_detections = args.max_detections
 
    np_outputs = imx500.get_outputs(metadata, add_batch=True)
    input_w, input_h = imx500.get_input_size()
    if np_outputs is None:
        return None
 
    if intrinsics.postprocess == "nanodet":
        boxes, scores, classes = postprocess_nanodet_detection(
            outputs=np_outputs[0], 
            conf=threshold, 
            iou_thres=iou,
            max_out_dets=max_detections
        )[0]
        boxes = scale_boxes(boxes, 1, 1, input_h, input_w, False, False)
    else:
        boxes, scores, classes = np_outputs[0][0], np_outputs[1][0], np_outputs[2][0]
        if bbox_normalization:
            boxes = boxes / input_h
        boxes = np.array_split(boxes, 4, axis=1)
        boxes = zip(*boxes)
 
    return [
        Detection(box, category, score, metadata)
        for box, score, category in zip(boxes, scores, classes)
        if score > threshold
    ]
 
@lru_cache
def get_labels():
    labels = intrinsics.labels
    if intrinsics.ignore_dash_labels:
        labels = [label for label in labels if label and label != "-"]
    return labels
 
def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, 
                        default="/home/UPtap/Desktop/UP-Tap/model/yolo_face_detect/model_imx_model/rpk_output/network.rpk")
    parser.add_argument("--fps", type=int)
    parser.add_argument("--bbox-normalization", action=argparse.BooleanOptionalAction)
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--iou", type=float, default=0.65)
    parser.add_argument("--max-detections", type=int, default=10)
    parser.add_argument("--ignore-dash-labels", action=argparse.BooleanOptionalAction)
    parser.add_argument("--postprocess", choices=["", "nanodet"], default=None)
    parser.add_argument("-r", "--preserve-aspect-ratio", action=argparse.BooleanOptionalAction)
    parser.add_argument("--labels", default="/home/UPtap/Desktop/UP-Tap/model/yolo_face_detect/model_imx_model/labels.txt", type=str)
    parser.add_argument("--print-intrinsics", action="store_true")
    return parser.parse_args()
 
if __name__ == "__main__":
    args = get_args()
    
    # Initialize Qt application
    app = QApplication([])
    
    # Create and run application wrapper
    wrapper = ApplicationWrapper(args)
    atexit.register(wrapper.cleanup)
    
    
    try:
        wrapper.run()
        app.exec()
    except KeyboardInterrupt:
        wrapper.cleanup()
        sys.exit(0)
    sys.exit()
