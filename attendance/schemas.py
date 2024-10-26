from ninja import Schema, ModelSchema
from datetime import date, time, datetime

class TimeInData(Schema):
    student_id: int
    subject_id: int

class TimeInResponse(Schema):
    time_in: time
    is_present: bool
    success: bool = True

class TimeInError(Schema):
    success: bool
    message: str