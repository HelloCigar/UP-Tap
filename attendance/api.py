from ninja import Router
from .models import AttendanceSheet, StudentAttendaceInfo
from .schemas import *
from teachers.models import Subjects
from students.models import Student
from datetime import date, datetime
from django.shortcuts import get_object_or_404
from .services import verify_face

router = Router()

@router.post("/time-in", response={200: TimeInResponse, 500: TimeInError})
def save_time_in(request, data: TimeInData):
    subject = get_object_or_404(Subjects, subject_id=data.subject_id)
    attendance_sheet, is_new_attendance = AttendanceSheet.objects.get_or_create(session_date=date.today(), subject_id=subject)
    student = get_object_or_404(Student, student_id=data.student_id)

    verified, error_response = verify_face(student.face_data, data.face_data)
    if not verified:
        return 500, error_response    

    attendance_info, is_new_info = StudentAttendaceInfo.objects.get_or_create(
        sheet_id=attendance_sheet,
        student_id=student,
    )

    if is_new_info:
        attendance_info.time_in = datetime.now().time()
        attendance_info.save()
        return attendance_info
    else:
        return 500, {"success": False, "message": "Student has already time-in!"}
    

@router.post("/time-out", response={200: TimeOutResponse, 500: TimeOutError})
def save_time_out(request, data: TimeOutData):
    subject = get_object_or_404(Subjects, subject_id=data.subject_id)
    attendance_sheet, is_new_attendance = AttendanceSheet.objects.get_or_create(session_date=date.today(), subject_id=subject)
    student = get_object_or_404(Student, student_id=data.student_id)

    verified, error_response = verify_face(student.face_data, data.face_data)
    if not verified:
        return 500, error_response

    attendance_info, is_new_info = StudentAttendaceInfo.objects.get_or_create(
        sheet_id=attendance_sheet,
        student_id=student,
    )

    if is_new_info:
        return 500, {"success": False, "message": "No attendance records found!"}
        
    elif attendance_info.time_out != None:
        return 500, {"success": False, "message": "Student has already time-out!"}
    
    else:
        attendance_info.time_out = datetime.now().time()
        attendance_info.is_present = True
        attendance_info.save()
        return attendance_info

    

    
        







