import os
from typing import Tuple, Union

from django.shortcuts import get_object_or_404
from django.utils import timezone
from attendance.models import AttendanceSheet, StudentAttendaceInfo
from students.models import Student, SubjectEnrollment
from teachers.models import Subjects
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1' 

from deepface import DeepFace

def verify_face(student_face_data, input_face_data):
    try:
        check_face = DeepFace.verify(student_face_data, input_face_data, anti_spoofing=True)
        if not check_face['verified']:
            return False, {"success": False, "message": "Face data mismatch!"}
        return True, None
    except ValueError:
        return False, {"success": False, "message": "Spoof image or no face detected!"}


def get_student_and_enrollment(student_id: str, subject_id: str) -> Tuple[Student, SubjectEnrollment]:
    """Get student and subject enrollment or raise appropriate errors."""
    student = get_object_or_404(Student, student_id=student_id)
    enrollment = get_object_or_404(SubjectEnrollment, student_id=student, subject_id=subject_id)
    return student, enrollment

def process_attendance(student: Student, subject: Subjects, face_data: str, is_time_in: bool) -> Union[StudentAttendaceInfo, dict]:
    """Process attendance for time-in or time-out."""
    today = timezone.now().date()
    attendance_sheet, _ = AttendanceSheet.objects.get_or_create(session_date=today, subject_id=subject)

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