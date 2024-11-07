from ninja import Router
from .models import AttendanceSheet, StudentAttendaceInfo
from .schemas import *
from teachers.models import Subjects
from students.models import Student, SubjectEnrollment
from datetime import date, datetime
from django.shortcuts import get_object_or_404
from .services import verify_face
from typing import List

router = Router()

@router.post("/time-in", response={200: TimeInResponse, 206: TimeInError})
def save_time_in(request, data: TimeInData):
    subject = get_object_or_404(Subjects, subject_id=data.subject_id)
    attendance_sheet, is_new_attendance = AttendanceSheet.objects.get_or_create(session_date=date.today(), subject_id=subject)
    try:
        student = Student.objects.get(student_id=data.student_id)
    except:
        return 206, {"success": False, "message": "Student not registered!"}
    
    try:
        subject_enrollment = SubjectEnrollment.objects.get(student_id=student, subject_id=subject)
    except:
        return 206, {"success": False, "message": "Student is not enrolled in this subject!"}


    verified, error_response = verify_face(student.face_data, data.face_data)
    if not verified:
        return 206, error_response    

    attendance_info, is_new_info = StudentAttendaceInfo.objects.get_or_create(
        sheet_id=attendance_sheet,
        student_id=student,
    )

    if is_new_info:
        attendance_info.time_in = datetime.now().time()
        attendance_info.save()
        return attendance_info
    else:
        return 206, {"success": False, "message": "Student has already time-in!"}
    

@router.post("/time-out", response={200: TimeOutResponse, 206: TimeOutError})
def save_time_out(request, data: TimeOutData):
    subject = get_object_or_404(Subjects, subject_id=data.subject_id)
    attendance_sheet, is_new_attendance = AttendanceSheet.objects.get_or_create(session_date=date.today(), subject_id=subject)

    try:
        student = Student.objects.get(student_id=data.student_id)
    except:
        return 206, {"success": False, "message": "Student not registered!"}
    
    try:
        subject_enrollment = SubjectEnrollment.objects.get(student_id=student, subject_id=subject)
    except:
        return 206, {"success": False, "message": "Student is not enrolled in this subject!"}

    verified, error_response = verify_face(student.face_data, data.face_data)
    if not verified:
        return 206, error_response

    attendance_info, is_new_info = StudentAttendaceInfo.objects.get_or_create(
        sheet_id=attendance_sheet,
        student_id=student,
    )

    if is_new_info:
        attendance_info.delete()  # Cancel the creation by deleting the new instance
        attendance_info = None
        return 206, {"success": False, "message": "No attendance records found! Please time in!"}
        
    elif attendance_info.time_out != None:
        return 206, {"success": False, "message": "Student has already time-out!"}
    
    else:
        attendance_info.time_out = datetime.now().time()
        attendance_info.is_present = True
        attendance_info.save()
        return attendance_info


@router.get("/recent", response={200: List[RecentTimeInResponse], 201: List[RecentTimeOutResponse], 206: RecentError})
def get_recent_attendance(request, type: str):
    if type == 'time_out':
        recent_attendance_info = StudentAttendaceInfo.objects.filter(time_out__isnull=False).order_by('-sheet_id__session_date', f'-{type}')[:5]
    else:
        recent_attendance_info = StudentAttendaceInfo.objects.all().order_by('-sheet_id__session_date', f'-{type}')[:5]

    if len(recent_attendance_info) == 0:
        return 206, {"success": False, "message": "No recent attendance records found!"}

    elif type == 'time_in':
        #return response code and list of dictionaries
        return 200, recent_attendance_info

    elif type == 'time_out':
        return 201, recent_attendance_info

    

    
        







