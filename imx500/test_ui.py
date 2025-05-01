import sys, base64, threading
from functools import lru_cache

import cv2
import numpy as np
import requests
from picamera2 import MappedArray, Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import NetworkIntrinsics, postprocess_nanodet_detection
# Use PySide6-compatible GL widget
from picamera2.previews.qt import QGlSide6Picamera2 as QGlPicamera2
from PySide6.QtCore import QTimer, Qt, QThread, Signal, QRegularExpression
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout,
    QLineEdit, QLabel, QComboBox,
)

# ---------- IMX500 Detection Utilities ----------
@lru_cache
def get_labels(intrinsics: NetworkIntrinsics):
    labels = intrinsics.labels or []
    if intrinsics.ignore_dash_labels:
        labels = [l for l in labels if l and l != "-"]
    return labels


def parse_detections(metadata: dict, imx500: IMX500, intrinsics: NetworkIntrinsics):
    outputs = imx500.get_outputs(metadata, add_batch=True)
    if outputs is None:
        return []
    threshold = intrinsics.conf_threshold
    iou = intrinsics.iou_threshold
    max_dets = intrinsics.max_detections
    if intrinsics.postprocess == 'nanodet':
        boxes, scores, classes = postprocess_nanodet_detection(
            outputs[0][0], conf=threshold, iou_thres=iou, max_out_dets=max_dets
        )[0]
        from picamera2.devices.imx500.postprocess import scale_boxes
        h, w = imx500.get_input_size()
        boxes = scale_boxes(boxes, 1, 1, h, w, False, False)
    else:
        b, s, c = outputs[0][0], outputs[1][0], outputs[2][0]
        if intrinsics.bbox_normalization:
            b = b / imx500.get_input_size()[1]
        coords = np.split(b, 4, axis=1)
        boxes = list(zip(*coords))
        scores, classes = s, c
    detections = [
        (int(x), int(y), int(w), int(h), int(cat), float(conf))
        for (x, y, w, h), conf, cat in zip(boxes, scores, classes)
        if conf >= threshold
    ]
    return detections

# ---------- Worker Thread for Posting ----------
class PostWorker(QThread):
    finished = Signal(str)

    def __init__(self, rfid: str, face_jpg: bytes, endpoint: str, parent=None):
        super().__init__(parent)
        self.rfid = rfid
        self.face_jpg = face_jpg
        self.endpoint = endpoint

    def run(self):
        try:
            b64 = base64.b64encode(self.face_jpg).decode('utf-8')
            payload = {"student_id": int(self.rfid), "face_data": b64}
            headers = {"Authorization": "Bearer 99cbb9718d1c98f66d5a99372a4782ed9206ddd6"}
            url = f"http://127.0.0.1:8000/api/attendance/{self.endpoint}"
            res = requests.post(url, json=payload, headers=headers)
            res.raise_for_status()
            data = res.json()
            if data.get('success'):
                key = 'time_in' if self.endpoint == 'time-in' else 'time_out'
                self.finished.emit(
                    f"{self.endpoint.replace('-', ' ').title()} @ {data.get(key)} - {data.get('student_name')}"
                )
            else:
                self.finished.emit(data.get('message', 'Unknown response'))
        except Exception as e:
            self.finished.emit(f"Error: {e}")

# ---------- Main Application ----------
class MainWindow(QMainWindow):
    def __init__(self, model_path, inference_rate=20):
        super().__init__()
        self.setWindowTitle("UPTap Attendance (IMX500)")

        # Setup IMX500 and Picamera2
        self.imx500 = IMX500(model_path)
        self.intr = self.imx500.network_intrinsics or NetworkIntrinsics()
        self.intr.update_with_defaults()
        self.picam2 = Picamera2(self.imx500.camera_num)

        # Embed camera preview widget
        self.preview = QGlPicamera2(self.picam2, width=640, height=480, keep_ar=True)

        # Start camera
        self.picam2.start(self.picam2.create_preview_configuration(
            {'format': 'RGB888'}, controls={'FrameRate': self.intr.inference_rate}
        ), show_preview=False)

        # UI Elements
        self.endpoint_selector = QComboBox()
        self.endpoint_selector.addItem("Time In", "time-in")
        self.endpoint_selector.addItem("Time Out", "time-out")
        self.rfid_input = QLineEdit()
        self.rfid_input.setMaxLength(10)
        self.rfid_input.setPlaceholderText("Scan RFID…")
        self.rfid_input.setValidator(QRegularExpressionValidator(
            QRegularExpression("\d+"), self))
        self.rfid_input.hide()
        self.rfid_input.returnPressed.connect(self.on_rfid)
        self.status_label = QLabel("", alignment=Qt.AlignCenter)
        self.status_label.setStyleSheet("color:black;")

        # Layout
        layout = QVBoxLayout()
        for w in (self.preview, self.endpoint_selector, self.rfid_input, self.status_label):
            layout.addWidget(w)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Detection timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.process_detections)
        self.timer.start(int(1000/inference_rate))
        self._last_count = 0
        self.current_face = None

    def set_status(self, msg, kind='info'):
        cmap = {'info':'black','success':'green','warning':'orange','error':'red'}
        self.status_label.setStyleSheet(f"color:{cmap.get(kind,'black')};")
        self.status_label.setText(msg)

    def process_detections(self):
        req = self.picam2.capture_request()
        meta = req.get_metadata()
        dets = parse_detections(meta, self.imx500, self.intr)
        # draw overlay RGBA
        overlay = np.zeros((480,640,4), dtype=np.uint8)
        faces = []
        for x,y,w,h,cat,conf in dets:
            if get_labels(self.intr)[cat]=='person':
                faces.append((x,y,w,h))
                cv2.rectangle(overlay,(x,y),(x+w,y+h),(0,255,0,150),2)
        self.preview.add_overlay(overlay)
        req.release()
        # UI logic same as before
        cnt = len(faces)
        if cnt>1:
            self.rfid_input.hide(); self.set_status("Multiple people","warning")
        elif cnt==1:
            if self._last_count!=1:
                self.rfid_input.clear(); self.rfid_input.show(); self.rfid_input.setFocus();
                self.set_status("","info"); self.current_face = faces[0]
        else:
            self.rfid_input.hide(); self.set_status("","info")
        self._last_count = cnt

    def on_rfid(self):
        text = self.rfid_input.text()
        if len(text)!=10:
            self.set_status("RFID must be 10 digits","error"); return
        self.rfid_input.setDisabled(True); self.set_status("Posting...","info")
        x,y,w,h = self.current_face
        req = self.picam2.capture_request()
        with MappedArray(req,'main') as m:
            roi = m.array[y:y+h, x:x+w]
        req.release()
        ok,j = cv2.imencode('.jpg', cv2.cvtColor(roi, cv2.COLOR_RGB2BGR))
        if not ok:
            self.set_status("Encode error","error"); self.rfid_input.setEnabled(True); return
        endpt = self.endpoint_selector.currentData()
        worker = PostWorker(text, j.tobytes(), endpt, self)
        worker.finished.connect(lambda m: self.set_status(m,'success' if ' @ ' in m else 'error'))
        worker.finished.connect(lambda _: self.reset_input())
        worker.start()

    def reset_input(self):
        self.rfid_input.clear(); self.rfid_input.setEnabled(True)
        QTimer.singleShot(4000, lambda: self.set_status("","info"))
        self.rfid_input.show(); self.rfid_input.setFocus()

    def closeEvent(self, e):
        self.picam2.stop()
        super().closeEvent(e)

if __name__=='__main__':
    app = QApplication(sys.argv)
    model = "/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk"
    win = MainWindow(model)
    win.show(); sys.exit(app.exec_())
