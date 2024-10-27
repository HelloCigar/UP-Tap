from ninja import Schema, ModelSchema
from datetime import date, time, datetime

class TimeInData(Schema):
    student_id: int
    subject_id: int
    face_data: str

class TimeInResponse(Schema):
    time_in: time
    success: bool = True

class TimeInError(Schema):
    success: bool
    message: str

class TimeOutData(TimeInData):
    pass

class TimeOutResponse(TimeInResponse):
    time_out: time
    is_present: bool

class TimeOutError(TimeInError):
    pass