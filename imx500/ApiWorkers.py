
from PyQt5.QtCore import QThread, pyqtSignal
import requests

class TimeInWorker(QThread):
    # index, success flag, message (error or empty), student_name (or ""), time_in (or "")
    finished = pyqtSignal(int, bool, str, str, str)

    def __init__(self, index: int, student_id: int, face_data: str):
        super().__init__()
        self.index = index
        self.student_id = student_id
        self.face_data = face_data

    def run(self):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/attendance/time-in",
                json={
                    "rfid": self.student_id,
                    "face_data": self.face_data
                },
                headers={
                    "Authorization" : "Bearer ae8b38a36238ffbce630250a9b37727589e635ba"
                },
                timeout=5
            )
            payload = response.json()
            # 200 → success:true + time_in + student_name
            if response.status_code == 200 and payload.get("success", True):
                self.finished.emit(
                    self.index,
                    True,
                    "",
                    payload.get("student_name", ""),
                    payload.get("time_in", "")
                )
            else:
                # 206 or any other non‑200 → success:false + message
                self.finished.emit(
                    self.index,
                    False,
                    payload.get("message", "Verification failed"),
                    "",
                    ""
                    )
        except Exception as e:
            self.finished.emit(self.index, False, str(e), "", "")

class TimeOutWorker(TimeInWorker):
    def run(self):
        try:
            response = requests.post(
                "http://127.0.0.1:8000/api/attendance/time-out",
                json={
                    "rfid": self.student_id,
                    "face_data": self.face_data
                },
                headers={
                    "Authorization" : "Bearer ae8b38a36238ffbce630250a9b37727589e635ba"
                },
                timeout=5
            )
            payload = response.json()
            # 200 → success:true + time_in + student_name
            if response.status_code == 200 and payload.get("success", True):
                self.finished.emit(
                    self.index,
                    True,
                    "",
                    payload.get("student_name", ""),
                    payload.get("time_out", "")
                )
            else:
                # 206 or any other non‑200 → success:false + message
                self.finished.emit(
                    self.index,
                    False,
                    payload.get("message", "Verification failed"),
                    "",
                    ""
                    )
        except Exception as e:
            self.finished.emit(self.index, False, str(e), "", "")
