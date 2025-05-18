import logging
from ninja import Router
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from django.utils import timezone
from typing import List, Tuple, Union
from .models import AttendanceSheet, StudentAttendaceInfo
from django.db.models import Q
from .schemas import StudentAttendanceSchema, TimeInData, TimeOutData, TimeInResponse, TimeOutResponse, TimeInError, TimeOutError, RecentTimeInResponse, RecentTimeOutResponse, RecentError
from teachers.models import Subjects
from .services import process_attendance, get_student_and_active_subject 
from django_eventstream import send_event


router = Router()


@router.post("/time-in", response={200: TimeInResponse, 206: TimeInError})
def save_time_in(request, data: TimeInData):
    print("Time In Data:", data)
    """Handle time-in requests."""
    try:
        student, subject, attendance_sheet = get_student_and_active_subject(data.rfid, request.user)
    except Exception as e:
        return 206, {"success": False, "message": str(e)}

    result = process_attendance(student, subject, data.face_data, attendance_sheet=attendance_sheet, is_time_in=True)
    if isinstance(result, StudentAttendaceInfo):
        data = {
            "time_in": result.time_in.isoformat(),
            "subject_name": f'{result.sheet_id.subject_id.subject_name}',
            "student_name": f'{result.student_id.first_name} {result.student_id.last_name}',
            "date": result.sheet_id.session_date
        }
        send_event("attendance", "time_in", data)
    return (200, result) if isinstance(result, StudentAttendaceInfo) else (206, result)

@router.post("/time-out", response={200: TimeOutResponse, 206: TimeOutError})
def save_time_out(request, data: TimeOutData):
    """Handle time-out requests."""
    try:
        student, subject, attendance_sheet = get_student_and_active_subject(data.rfid, request.user)
    except Exception as e:
        return 206, {"success": False, "message": str(e)}

    result = process_attendance(student, subject, data.face_data, attendance_sheet, False)
    if isinstance(result, StudentAttendaceInfo):
        data = {
            "time_out": result.time_out.isoformat(),
            "subject_name": f'{result.sheet_id.subject_id.subject_name}',
            "student_name": f'{result.student_id.first_name} {result.student_id.last_name}',
            "date": result.sheet_id.session_date
        }
        send_event("attendance", "time_out", data)
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


from typing import Optional
from ninja import Schema
class FilterSchema(Schema):
    subject_ids: List[int] = None
    is_present: List[bool] = None

@router.post("/all", response={200: List[StudentAttendanceSchema], 206: RecentError})
def get_all_student_attendance(request, 
        start_date: str = None, 
        end_date: str = None, 
        q: str = None,
        filter: FilterSchema = None,
    ):

    attendance_records = StudentAttendaceInfo.objects.all()

    if not request.user.is_superuser:
        attendance_records = attendance_records.filter(
            student_id__enrollments__subject_id__teacher=request.user
        )

    if filter.subject_ids:
        try:
            attendance_records = attendance_records.filter(sheet_id__subject_id__in=filter.subject_ids)
        except Exception as e:
            return 206, {"success": False, "message": str(e)}
    
    if filter.is_present:
        attendance_records = attendance_records.filter(is_present__in=filter.is_present)
    
    if start_date:
        try:
            start_date = timezone.datetime.strptime(start_date, "%Y-%m-%d").date()
            attendance_records = attendance_records.filter(sheet_id__session_date__gte=start_date)
        except Exception as e:
            return 206, {"success": False, "message": str(e)}
    
    if end_date:
        try:
            end_date = timezone.datetime.strptime(end_date, "%Y-%m-%d").date()
            attendance_records = attendance_records.filter(sheet_id__session_date__lte=end_date)
        except Exception as e:
            return 206, {"success": False, "message": str(e)}
    
    if q:
        attendance_records = attendance_records.filter(
            Q(student_id__first_name__icontains=q) |
            Q(student_id__last_name__icontains=q) |
            Q(sheet_id__subject_id__subject_name__icontains=q)
        )

    attendance_records = attendance_records.select_related('student_id', 'sheet_id__subject_id').order_by(
        '-sheet_id__session_date', '-time_in'
    ).distinct()

    if not attendance_records:
        return 206, {"success": False, "message": "No attendance records found!"}

    return 200, attendance_records
