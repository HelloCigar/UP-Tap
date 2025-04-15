import os
from typing import Tuple, Union
from model.inference import verify_face_similarity
from django.shortcuts import get_object_or_404
from django.utils import timezone
from attendance.models import AttendanceSheet, StudentAttendaceInfo
from students.models import Student, SubjectEnrollment
from teachers.models import Subjects
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' 
import logging
from deepface import DeepFace

def verify_face(student_face_data, input_face_data):
    try:
        is_face_similar = verify_face_similarity(student_face_data, input_face_data)
        logging.info("is_face_similar: ", is_face_similar)
        if not is_face_similar:
            return False, {"success": False, "message": "Face data mismatch!"}
        return True, None
    except ValueError:
        logging.error("ValueError: ", ValueError)
        return False, {"success": False, "message": "Spoof image or no face detected!"}


def get_student_and_enrollment(student_id: str, subject_id: str) -> Tuple[Student, SubjectEnrollment]:
    """Get student and subject enrollment or raise appropriate errors."""
    student = get_object_or_404(Student, student_id=student_id)
    enrollment = get_object_or_404(SubjectEnrollment, student_id=student, subject_id=subject_id)
    return student, enrollment

def process_attendance(student: Student, subject: Subjects, face_data: str, attendance_sheet: AttendanceSheet, is_time_in: bool) -> Union[StudentAttendaceInfo, dict]:
    """Process attendance for time-in or time-out."""
    today = timezone.now().date()

    verified, error_response = verify_face(student.face_data, face_data)
    if not verified:
        return error_response

    attendance_info, created = StudentAttendaceInfo.objects.get_or_create(
        sheet_id=attendance_sheet,
        student_id=student,
    )

    if is_time_in:
        if created:
            attendance_info.time_in = timezone.now().time()
            attendance_info.save()
            return attendance_info
        return {"success": False, "message": "Student has already timed in!"}
    else:
        if created:
            attendance_info.delete()
            return {"success": False, "message": "No attendance records found! Please time in!"}
        if attendance_info.time_out:
            return {"success": False, "message": "Student has already timed out!"}
        attendance_info.time_out = timezone.now().time()
        attendance_info.is_present = True
        attendance_info.save()
        return attendance_info
    
from datetime import datetime, timedelta
from django.utils import timezone
from teachers.models import ClassSchedule

def get_student_and_active_subject(student_id: str) -> Tuple[Student, Subjects, AttendanceSheet]:
    """Get student, active subject, and attendance sheet or raise appropriate errors."""
    student = get_object_or_404(Student, student_id=student_id)
    
    # Get the current time and day
    now = timezone.now()
    today = now.strftime("%A")
    current_time = now.time()

    # Convert the current time to a datetime object before adding the timedelta
    current_datetime = datetime.combine(now.date(), current_time)
    adjusted_time = (current_datetime + timedelta(minutes=10)).time()


    # Find an active class based on schedule
    active_schedule = ClassSchedule.objects.filter(
        day_of_week=today,
        start_time__lte=adjusted_time,
        end_time__gte=current_time
    ).select_related('subject_id').first()

    if not active_schedule:
        raise ValueError("No active class session found at this time!")

    # Check if student is enrolled in this subject
    enrollment = get_object_or_404(
        SubjectEnrollment, 
        student_id=student, 
        subject_id=active_schedule.subject_id
    )

    # Get or create the AttendanceSheet for today
    attendance_sheet, _ = AttendanceSheet.objects.get_or_create(
        session_date=now.date(), 
        subject_id=active_schedule.subject_id
    )

    return student, active_schedule.subject_id, attendance_sheet
