from ninja import Schema, ModelSchema
from datetime import date, time, datetime
from typing import Optional
from attendance.models import StudentAttendaceInfo

class TimeInData(Schema):
    rfid: int
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

class StudentAttendanceSchema(Schema):
    attendance_info_id: int
    is_present: bool
    time_in: Optional[str] = None
    time_out: Optional[str] = None
    sheet_id: int
    student_name: str
    subject_name: str
    session_date: date

    
    @staticmethod
    def resolve_student_name(obj):
        return f'{obj.student_id.first_name} {obj.student_id.last_name}'
    
    @staticmethod
    def resolve_subject_name(obj):
        return f'{obj.sheet_id.subject_id.subject_name}'
    
    @staticmethod
    def resolve_session_date(obj):
        return obj.sheet_id.session_date
    
    @staticmethod
    def resolve_sheet_id(obj):
        return obj.sheet_id.sheet_id

    @staticmethod
    def resolve_time_in(obj):
        return obj.time_in.strftime("%I:%M %p") if obj.time_in else None
    
    @staticmethod
    def resolve_time_out(obj):
        return obj.time_out.strftime("%I:%M %p") if obj.time_out else None

