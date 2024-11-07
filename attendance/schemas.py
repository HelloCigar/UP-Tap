from ninja import Schema, ModelSchema
from datetime import date, time, datetime
from typing import Optional

class TimeInData(Schema):
    student_id: int
    subject_id: int
    face_data: str

class TimeInResponse(Schema):
    time_in: time
    success: bool = True
    student_name: Optional[str] = None

    @staticmethod
    def resolve_student_name(obj):
        return f'{obj.student_id.first_name} {obj.student_id.last_name}'


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

class RecentTimeInResponse(Schema):
    time_in: time
    subject_name: Optional[str] = None
    student_name: Optional[str] = None
    date: date

    @staticmethod
    def resolve_student_name(obj):
        return f'{obj.student_id.first_name} {obj.student_id.last_name}'

    @staticmethod
    def resolve_subject_name(obj):
        return f'{obj.sheet_id.subject_id.subject_name}'
    
    @staticmethod
    def resolve_date(obj):
        return obj.sheet_id.session_date

class RecentTimeOutResponse(RecentTimeInResponse):
    time_out: time


class RecentError(TimeInError):
    pass