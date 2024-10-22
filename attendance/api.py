from ninja import Schema, ModelSchema
from ninja import Router
from .models import AttendanceSheet, StudentAttendaceInfo
from teachers.models import Subjects
from students.models import Student
from datetime import date

router = Router()

class CheckTimeIn(Schema):
    student_id: int
    #change to id
    subject_name: str
    session_date: date

class ReturnTimeIn(Schema):
    is_present: bool

@router.post("/check-time-in/", response=ReturnTimeIn)
def get_student_time_in(request, data: CheckTimeIn):
    student = Student.objects.get(student_id=data.student_id)
    subject = Subjects.objects.get(subject_name=data.subject_name, teacher_id=request.user)
    sheet = AttendanceSheet.objects.get(session_date=data.session_date, subject_id=subject)
    attendance_info = StudentAttendaceInfo.objects.get(sheet_id=sheet, student_id=student)
    
    return attendance_info






