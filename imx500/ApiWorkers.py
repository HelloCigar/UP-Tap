
from PyQt5.QtCore import QThread, pyqtSignal
import requests

def get_new_token() -> str | None:
    try:
        response = requests.get("http://127.0.0.1:8000/api/teachers/latest_token/", timeout=5)
        response.raise_for_status()
        payload = response.json()
        return payload.get("token")
    except Exception as e:
        print(f"Failed to refresh token: {e}")
        return None


class TimeInWorker(QThread):
    # index, success flag, message (error or empty), student_name (or ""), time_in (or "")
    finished = pyqtSignal(int, bool, str, str, str)

    def __init__(self, index: int, student_id: int, face_data: str):
        super().__init__()
        self.index = index
        self.student_id = student_id
        self.face_data = face_data
        self.token = '8c89bd60a7e5343d46a4f587615ff169b5afaf74'

    def run(self):
        try:
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            response = requests.post(
                self.endpoint,
                json={
                    "rfid": self.student_id,
                    "face_data": self.face_data
                },
                headers=headers,
                timeout=5
            )
            if response.status_code == 401:
                # Token expired, attempt to refresh
                new_token = get_new_token()
                if new_token:
                    self.token = new_token
                    headers["Authorization"] = f"Bearer {self.token}"
                    response = requests.post(
                        self.endpoint,
                        json={
                            "rfid": self.student_id,
                            "face_data": self.face_data
                        },
                        headers=headers,
                        timeout=5
                    )
                else:
                    self.finished.emit(self.index, False, "Failed to refresh token", "", "")
                    return

            payload = response.json()
            if response.status_code == 200 and payload.get("success", True):
                self.finished.emit(
                    self.index,
                    True,
                    "",
                    payload.get("student_name", ""),
                    payload.get("time_in", "") if hasattr(self, 'time_in') else payload.get("time_out", "")
                )
            else:
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
            headers = {
                "Authorization": f"Bearer {self.token}"
            }
            response = requests.post(
                self.endpoint,
                json={
                    "rfid": self.student_id,
                    "face_data": self.face_data
                },
                headers=headers,
                timeout=5
            )
            if response.status_code == 401:
                # Token expired, attempt to refresh
                new_token = get_new_token()
                if new_token:
                    self.token = new_token
                    headers["Authorization"] = f"Bearer {self.token}"
                    response = requests.post(
                        self.endpoint,
                        json={
                            "rfid": self.student_id,
                            "face_data": self.face_data
                        },
                        headers=headers,
                        timeout=5
                    )
                else:
                    self.finished.emit(self.index, False, "Failed to refresh token", "", "")
                    return

            payload = response.json()
            if response.status_code == 200 and payload.get("success", True):
                self.finished.emit(
                    self.index,
                    True,
                    "",
                    payload.get("student_name", ""),
                    payload.get("time_in", "") if hasattr(self, 'time_in') else payload.get("time_out", "")
                )
            else:
                self.finished.emit(
                    self.index,
                    False,
                    payload.get("message", "Verification failed"),
                    "",
                    ""
                )
        except Exception as e:
            self.finished.emit(self.index, False, str(e), "", "")


