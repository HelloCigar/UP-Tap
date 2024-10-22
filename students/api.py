from ninja import Schema, ModelSchema
from ninja import Router
from typing import List
from .models import Student, SubjectEnrollment
from teachers.models import Subjects
from ninja.pagination import paginate
from django.db.models import Q
from django.db.utils import IntegrityError


router = Router()

class StudentSchema(ModelSchema):
    class Meta:
        model = Student
        fields = "__all__"

class StudentListSchema(ModelSchema):
    class Meta:
        model = Student
        exclude = ["face_data"]

@router.post("/register")
def register_student(request, data: StudentSchema, subjects: str):
    """
    Register a new student.

    Parameters:
        data (StudentSchema): The student data

    Returns:
        dict: A dictionary with the student_id of the newly created student
    """
    try:
        student = Student.objects.create(**data.dict())
    except IntegrityError:
        return {"error": "Student already exists!"}
    
    # add enrollment to connect subjects to students
    subjects = subjects[1:-1].split(',')
    for subject in subjects:
        subject = Subjects.objects.get(subject_id=subject)
        SubjectEnrollment.objects.create(student_id=student, subject_id=subject)


    return {"success": "Student information saved to the database!"}

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
            Q(student_id__icontains=q)
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



