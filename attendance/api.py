from ninja import Router
from .models import AttendanceSheet, StudentAttendaceInfo
from .schemas import *
from teachers.models import Subjects
from students.models import Student
from datetime import date, time, datetime
from django.shortcuts import get_object_or_404

router = Router()
    
@router.post("/check-time-in/", response=TimeInResponse)
def get_student_time_in(request, data: TimeInData):
    student = Student.objects.get(student_id=data.student_id)
    subject = Subjects.objects.get(subject_id=data.subject_id, teacher_id=request.user)
    sheet = AttendanceSheet.objects.get(session_date=data.session_date, subject_id=subject)
    attendance_info = StudentAttendaceInfo.objects.get(sheet_id=sheet, student_id=student)
    
    return attendance_info

@router.post("/time-in", response={200: TimeInResponse, 500: TimeInError})
def save_time_in(request, data: TimeInData):
    subject = get_object_or_404(Subjects, subject_id=data.subject_id)
    attendance_sheet, is_new_attendance = AttendanceSheet.objects.get_or_create(session_date=date.today(), subject_id=subject)
    student = get_object_or_404(Student, student_id=data.student_id)

    attendance_info, is_new = StudentAttendaceInfo.objects.get_or_create(
        sheet_id=attendance_sheet,
        student_id=student,
    )

    if is_new:
        attendance_info.time_in = datetime.now().time()
        attendance_info.save()
        return attendance_info
    else:
        return 500, {"success": False, "message": "Student already has time-in!"}

    

    
        







