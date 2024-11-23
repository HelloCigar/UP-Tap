from ninja import Router
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.utils import timezone
from typing import List, Tuple, Union
from .models import AttendanceSheet, StudentAttendaceInfo
from .schemas import TimeInData, TimeOutData, TimeInResponse, TimeOutResponse, TimeInError, TimeOutError, RecentTimeInResponse, RecentTimeOutResponse, RecentError
from teachers.models import Subjects
from students.models import Student, SubjectEnrollment
from .services import process_attendance, get_student_and_enrollment 


router = Router()

@router.post("/time-in", response={200: TimeInResponse, 206: TimeInError})
def save_time_in(request, data: TimeInData):
    """Handle time-in requests."""
    subject = get_object_or_404(Subjects, subject_id=data.subject_id)
    try:
        student, _ = get_student_and_enrollment(data.student_id, data.subject_id)
    except Exception as e:
        return 206, {"success": False, "message": str(e)}

    result = process_attendance(student, subject, data.face_data, is_time_in=True)
    return (200, result) if isinstance(result, StudentAttendaceInfo) else (206, result)

@router.post("/time-out", response={200: TimeOutResponse, 206: TimeOutError})
def save_time_out(request, data: TimeOutData):
    """Handle time-out requests."""
    subject = get_object_or_404(Subjects, subject_id=data.subject_id)
    try:
        student, _ = get_student_and_enrollment(data.student_id, data.subject_id)
    except Exception as e:
        return 206, {"success": False, "message": str(e)}

    result = process_attendance(student, subject, data.face_data, is_time_in=False)
    return (200, result) if isinstance(result, StudentAttendaceInfo) else (206, result)

@router.get("/recent", response={200: List[RecentTimeInResponse], 201: List[RecentTimeOutResponse], 206: RecentError})
def get_recent_attendance(request, type: str):
    """Get recent attendance records."""
    if type not in ['time_in', 'time_out']:
        return 206, {"success": False, "message": "Invalid record type!"}

    teacher = request.user
    queryset = StudentAttendaceInfo.objects.filter(
        student_id__enrollments__subject_id__teacher=teacher
    ).select_related('student_id', 'sheet_id__subject_id').order_by(
        '-sheet_id__session_date', f'-{type}'
    ).distinct()

    if type == 'time_out':
        queryset = queryset.filter(time_out__isnull=False)

    recent_attendance_info = queryset[:5]

    if not recent_attendance_info:
        return 206, {"success": False, "message": "No recent attendance records found!"}

    return (200 if type == 'time_in' else 201), recent_attendance_info