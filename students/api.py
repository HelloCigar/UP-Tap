from ninja import Router, PatchDict
from typing import List
from .models import UPRFID, Student, SubjectEnrollment
from teachers.models import Subjects
from ninja.pagination import paginate
from django.db.models import Q
from django.db.utils import IntegrityError
from .schemas import *
from django.db import transaction
from django.shortcuts import get_object_or_404

router = Router()

@router.post("/register", auth=None, response={200: StudentOut})
def register_student(request, data: StudentIn):
    """
    Register a new student.

    Parameters:
        data (StudentSchema): The student data

    Returns:
        dict: A dictionary with the student_id of the newly created student
    """
    student, created = Student.objects.update_or_create(
        student_id=data.student_id,
        defaults={
            "first_name": data.first_name or "",
            "middle_initial": data.middle_initial or "",
            "last_name": data.last_name or "",
            "email": data.email,
            "alt_email": data.alt_email,
            "course": data.course or "",
            "gender": data.gender or "",
            "face_data": data.face_data,
        }
    )

    desired = set(data.subject_ids)
    existing_qs = SubjectEnrollment.objects.filter(student_id=student)
    existing = set(existing_qs.values_list("subject_id", flat=True))
    
    to_add    = desired - existing
    to_remove = existing - desired

    with transaction.atomic():
        # 3. Delete enrollments that are no longer desired
        if to_remove:
            SubjectEnrollment.objects.filter(
                student_id=student, subject_id__in=to_remove
            ).delete()

        # 4. Create missing enrollments
        for subj_id in to_add:
            subj = Subjects.objects.get(pk=subj_id)
            SubjectEnrollment.objects.create(student_id=student, subject_id=subj)
    
    return student

@router.get("/all", response=List[StudentListSchema])
@paginate
def get_all_students(request, q: str = '', sort: str = 'student_id', order: str = 'asc', subjects: str = '[]'):
    """
    Get all students that are enrolled in any of the subjects
    that the authenticated user is a teacher of.

    Parameters:
        q (str): Optional search query to filter the result
        sort (str): Optional sort key (default is 'student_id')
        order (str): Optional sort order (default is 'asc')
        subjects (str): Optional string of comma-separated subject IDs
            (default is an empty string)

    Returns:
        List[StudentSchema]: A list of StudentSchema objects
    """

    teacher = request.user
    students = Student.objects.filter(enrollments__subject_id__teacher=teacher).distinct()

    if q:
        students = students.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(student_id__icontains=q) |
            Q(course__icontains=q) |
            Q(alt_email__icontains=q) |
            Q(enrollments__subject_id__subject_name__icontains=q)
        )
    # filter by subjects, format is string of [1, 2, 3]
    if subjects != '[]':
        # remove [ and ] first
        subjects = subjects[1:-1]
        students = students.filter(enrollments__subject_id__in=subjects.split(','))


    if sort:
        if order == 'asc':
            students = students.order_by(sort)
        else:
            students = students.order_by(f'-{sort}')

    return students


@router.get("/{student_id}", response=StudentSchema)
def get_student(request, student_id: int):
    return get_object_or_404(Student, student_id=student_id)



@router.put("/{student_id}")
def edit_student(request, student_id: int, data: PatchDict[StudentSchema], subjects: str, rfid: str):
    """
    Register a new student.

    Parameters:
        data (StudentSchema): The student data

    Returns:
        dict: A dictionary with the student_id of the newly created student
    """
    try:
        student = Student.objects.get(student_id=student_id)

        for attr, value in data.items():
            setattr(student, attr, value)
        student.save()

        student_rfid = UPRFID.objects.get(student=student)
        student_rfid.rfid_num = rfid
        student_rfid.save()

    except Exception as e:
        return {"error": str(e)}
    
    subjects = subjects[1:-1].split(',')  # Convert to list if necessary
    subject_ids = [int(sub.strip()) for sub in subjects]  # Convert to integers if they are not already

    # Get the current enrollments for the student
    current_enrollments = SubjectEnrollment.objects.filter(student_id=student)
    current_subject_ids = set(enrollment.subject_id.subject_id for enrollment in current_enrollments)

    # Determine which enrollments need to be added and which need to be removed
    new_subject_ids = set(subject_ids) - current_subject_ids
    removed_subject_ids = current_subject_ids - set(subject_ids)

    # Create new enrollments
    for subject_id in new_subject_ids:
        SubjectEnrollment.objects.create(student_id=student, subject_id_id=subject_id)

    # Delete removed enrollments
    SubjectEnrollment.objects.filter(student_id=student, subject_id_id__in=removed_subject_ids).delete()

    return {"success": True, "message": "Student information updated!"}

@router.delete("/{student_id}")
def delete_student(request, student_id: int):
    """
    Delete a student.

    Parameters:
        student_id (int): The ID of the student to delete

    Returns:
        dict: A dictionary with a success message
    """
    try:
        student = Student.objects.get(student_id=student_id)
        student.delete()
    except Student.DoesNotExist:
        return {"success": False}
    return {"success": True}


